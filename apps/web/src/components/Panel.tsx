import type { ReactNode } from 'react';
import type { LucideIcon } from 'lucide-react';

interface PanelProps {
  title?: string;
  eyebrow?: string;
  icon?: LucideIcon;
  span?: 4 | 5 | 6 | 7 | 8 | 12;
  className?: string;
  children: ReactNode;
}

export function Panel({ title, eyebrow, icon: Icon, span = 12, className = '', children }: PanelProps) {
  return (
    <section className={`panel span${span} ${className}`.trim()}>
      {(title || eyebrow || Icon) && (
        <div className="panelTitle">
          {Icon && <Icon size={18} />}
          <div>
            {eyebrow && <div className="eyebrow">{eyebrow}</div>}
            {title && <h3>{title}</h3>}
          </div>
        </div>
      )}
      {children}
    </section>
  );
}

