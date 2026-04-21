/** 后端不可达（未启动、未穿透、断网等）时的全屏提示 */
const INTERFACE_LOGO_SRC = '/branding/tagent-interface-logo.png';

export default function BackendUnavailable() {
  return (
    <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center gap-6 bg-black px-6">
      <img
        src={INTERFACE_LOGO_SRC}
        alt="Tagent"
        className="max-w-[min(100%,320px)] w-auto h-auto object-contain select-none"
        width={320}
        height={120}
        decoding="async"
      />
      <p className="text-sm font-medium tracking-wide text-neutral-500 md:text-base">
        404 Not Found
      </p>
      <p className="max-w-lg text-center text-lg leading-relaxed text-neutral-300 md:text-xl">
        Oooopps... 看起来我的主人正在给我保养 :)
      </p>
    </div>
  );
}
