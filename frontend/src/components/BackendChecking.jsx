/** 首次探测后端连通性时的全黑占位（避免先闪主界面再切离线页） */
export default function BackendChecking() {
  return <div className="fixed inset-0 z-[100] bg-[var(--color-chat-bg)]" aria-hidden />;
}
