# Bitmap64 统一序列化

> **Page ID**: 1554286865
> **URL**: https://confluence.shopee.io/pages/viewpage.action?pageId=1554286865

背景
==

随着id升级，各系统中使用的bitmap需要升级至64位，在升级过程中发现各语言对于64位bitmap的序列化方式略有差异。

为了方便的进行计算和存储，与语言解耦，需要对序列化方式进行标准化。

C++ \ Go 版本
===========

使用面最广，最为统一的基础版本。

Roaring64NavigableMap 也使用拆分模式，将一个 long 类型数据，拆分为高32位与低32位，高32位代表索引，低32位存储到对应 RoaringBitmap 中，其内部是一个 TreeMap 类型的结构。

![image2022-12-21_10-55-35.png](https://confluence.shopee.io/download/attachments/1554286865/image2022-12-21_10-55-35.png)

序列化方式为：

![image2022-12-21_11-3-6.png](https://confluence.shopee.io/download/attachments/1554286865/image2022-12-21_11-3-6.png)

Clickhouse 版本
=============

Clickhouse对bitmap做了些许优化：

一、元素个数不多于32个时，使用array存储：

```
元素是否大于32个(1比特，此时记为0) + CountSize(4字节，记录元素个数) + Long(8字节) * n
```

二、元素个数大于32个时，使用原有序列化方式

```
元素是否大于32个(1比特，此时记为1) + SerializeTotalSize(VarInt，变长Int,记录数据字节数) + highToBitmap.size(8字节) + (key, Serialize(roaringBitmap)) * n
```

Java 版本
=======

![image2022-12-21_11-26-3.png](https://confluence.shopee.io/download/attachments/1554286865/image2022-12-21_11-26-3.png)

**注意：C++\Go\Clickhouse中使用小端序进行存储，Java默认是大端序，需要在序列化及反序列化中对此部分进行修改。（尤其对于数值类型）**

写clickhouse bitmap
------------------

def serialize(rb: Roaring64NavigableMap): ByteBuffer = {
// ck中rbm对小于32的基数进行了优化，使用smallset进行存放
if (rb.getLongCardinality <= 32) {
// the serialization structure of roaringbitmap in clickhouse: Byte(1), VarInt(SerializedSizeInBytes), ByteArray(RoaringBitmap)
// and long occupies 8 bytes
val bos1 = ByteBuffer.allocate(1 + 1 + 8 * rb.getIntCardinality)
val bos = if (bos1.order eq ByteOrder.LITTLE_ENDIAN) bos1 else bos1.slice.order(ByteOrder.LITTLE_ENDIAN)
bos.put(0.toByte)
bos.put(rb.getIntCardinality.toByte)
rb.toArray.foreach(i => bos.putLong(i))
bos
} else {
/**
* Java: 是否无符号(1) + highToBitmap.size(4) + (key, Serialize(roaringBitmap)) * n
* Clickhouse: 元素是否大于32个(1) + SerializeTotalSize(4) + highToBitmap.size(8) + (key, Serialize(roaringBitmap)) * n
* Clickhouse 需要使用ByteOrder.LITTLE_ENDIAN,包括所有数字类型
* totalSize = size((key, Serialize(roaringBitmap)) * n) + 8
* https://github.com/RoaringBitmap/CRoaring/blob/master/cpp/roaring64map.hh -- line 994 -- 8字节存储mapSize
* */
val dataSize = rb.serializedSizeInBytes().toInt - 5 + 8
val bos = ByteBuffer.allocate(1 + VarInt.varIntSize(dataSize) + dataSize)
bos.order(ByteOrder.LITTLE_ENDIAN)
bos.put(1.toByte)
VarInt.putVarInt(dataSize, bos)
val baos = new ByteArrayOutputStream()
rb.serialize2ck(new DataOutputStream(baos))
bos.put(baos.toByteArray)
bos
}
}
implicit class Roaring64NavigableMapToCk(rb64: Roaring64NavigableMap){
def serialize2ck(output: DataOutput): Unit ={
val highToBitmapField = new Roaring64NavigableMap().getClass.getDeclaredField("highToBitmap")
highToBitmapField.setAccessible(true)
val highToBitmap: util.NavigableMap[Integer, BitmapDataProvider] = highToBitmapField.get(rb64).asInstanceOf[util.NavigableMap[Integer, BitmapDataProvider]]
println(s"nbhighs counts: ${highToBitmap.size().toLong}")
output.write(ByteBuffer.allocate(8).order(ByteOrder.LITTLE_ENDIAN).putLong(highToBitmap.size().toLong).array)
import scala.collection.JavaConversions._
for (entry <- highToBitmap.entrySet) { //此处要用小端序
val tmp = ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(entry.getKey.intValue).array
output.write(tmp)
entry.getValue.serialize(output)
}
}
}

读Clickhouse bitmap
------------------

 def deserializer64Bm(bytes: Array[Byte]): Roaring64NavigableMap = {
if (bytes.length <= 1) {
return new Roaring64NavigableMap()
} else if (bytes(0).toInt == 0) {
val result = new Roaring64NavigableMap()
val counts = bytes(1).toInt
println(bytes.length - 2)
val longBytes = bytes.slice(2, bytes.length).sliding(8, 8)
for (i <- 0 until counts) {
result.add(ByteBuffer.wrap(longBytes.next()).order(ByteOrder.LITTLE_ENDIAN).getLong)
}
if (counts != result.getIntCardinality) {
throw new Exception(s"deserializer 64bitmap failed: bitmap < 32 counts ${result.getIntCardinality} does not match $counts!")
}
return result
} else if (bytes(0).toInt == 1) {
//小于32个，Array[Long]
val serBytesSize = VarInt.getVarInt(ByteBuffer.wrap(bytes.slice(1, 100)))
val countSize = VarInt.varIntSize(serBytesSize)
val dataSize = bytes.slice(1 + countSize, bytes.length)
val dis = new DataInputStream(new ByteArrayInputStream(dataSize))
val result = new Roaring64NavigableMap()
result.deserializeFromBytes(dis)
return result
}
new Roaring64NavigableMap()
}
implicit class Roaring64NavigableMapToCk(rb64: Roaring64NavigableMap) {
def deserializeFromBytes(input: DataInput): Unit = {
rb64.clear()
val highToBitmapField = new Roaring64NavigableMap().getClass.getDeclaredField("highToBitmap")
highToBitmapField.setAccessible(true)
val highToBitmapValue: util.NavigableMap[Integer, BitmapDataProvider] = new util.TreeMap(new Comparator[Integer]() {
override def compare(o1: Integer, o2: Integer): Int = Integer.compare(o1 + Integer.MIN_VALUE, o2 + Integer.MIN_VALUE)
})
val nbHighs = ByteBuffer.wrap(BigInt(input.readLong()).toByteArray).order(ByteOrder.LITTLE_ENDIAN).getLong()
println(s"nbHighs counts: $nbHighs")
for (i <- 0l until nbHighs) {
val highValue = input.readInt()
var high = 0
if(highValue == 0){
println("0需要特殊处理")
}else{
high = ByteBuffer.wrap(BigInt(highValue).toByteArray).order(ByteOrder.LITTLE_ENDIAN).getInt()
}
val provider = new RoaringBitmap
provider.deserialize(input)
highToBitmapValue.put(high, provider)
}
highToBitmapField.set(rb64, highToBitmapValue)
val signedLongs = new Roaring64NavigableMap().getClass.getDeclaredField("signedLongs")
signedLongs.setAccessible(true)
signedLongs.set(rb64, false)
val resetPerfHelpers = new Roaring64NavigableMap().getClass.getDeclaredMethod("resetPerfHelpers")
resetPerfHelpers.setAccessible(true)
resetPerfHelpers.invoke(rb64)
}
}
