/** 后端不可达（未启动、未穿透、断网等）时的全屏提示 */
export default function BackendUnavailable() {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black px-6">
      <p className="max-w-lg text-center text-lg leading-relaxed text-neutral-300 md:text-xl">
        Oooopps... 看起来我的主人正在给我保养 :)
      </p>
    </div>
  );
}
