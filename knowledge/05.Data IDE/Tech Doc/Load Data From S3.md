# Load Data From S3

> **Page ID**: 1118328455
> **URL**: https://confluence.shopee.io/pages/viewpage.action?pageId=1118328455

1.Update dependencies jars, beware of version of Hadoop, need to fix conflicts of jars

> ```
> <dependency>  
>     <groupId>software.amazon.awssdk</groupId>  
>     <artifactId>s3</artifactId>  
>     <version>2.16.60</version>  
> </dependency>  
>   
> <dependency>  
>     <groupId>org.apache.hadoop</groupId>  
>     <artifactId>hadoop-aws</artifactId>  
>     <version>${hadoop.version}</version>  
> </dependency>  
>   
> <dependency>  
>     <groupId>net.java.dev.jets3t</groupId>  
>     <artifactId>jets3t</artifactId>  
>     <version>0.9.4</version>  
> </dependency>
> ```

```
2.Use Latest hbase bulkload object
```

> ```
> val tool = new BulkLoadHFilesTool(hbaseConf)  
> tool.bulkLoad(tableName, new Path(hfilePath))
> ```

3.Git URL

<https://git.garena.com/shopee/seamoney-data/real-time/spark/hdfs2hbaseandredis.git>

![image2022-5-16_16-52-30.png](https://confluence.shopee.io/download/attachments/1118328455/image2022-5-16_16-52-30.png)
