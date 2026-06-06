import clsx from "clsx";

interface ConfirmModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmModal({ isOpen, title, message, onConfirm, onCancel }: ConfirmModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div 
        className="w-full max-w-sm rounded-[var(--radius-xl)] bg-[var(--bg-surface)] p-6 border border-[var(--border)] shadow-2xl animate-in fade-in zoom-in-95 duration-200"
      >
        <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">{title}</h3>
        <p className="text-sm text-[var(--text-secondary)] mb-6 leading-relaxed">
          {message}
        </p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded-[var(--radius-md)] text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 rounded-[var(--radius-md)] text-sm font-medium bg-red-500/10 text-red-500 hover:bg-red-500 hover:text-white transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
