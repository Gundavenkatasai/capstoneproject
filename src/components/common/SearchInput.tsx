import React, { useState, useEffect } from "react";
import { Search, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface SearchInputProps {
  placeholder?: string;
  value?: string;
  onChange?: (val: string) => void;
  className?: string;
  shortcut?: string;
}

export function SearchInput({
  placeholder = "Search grievances, categories, IDs...",
  value = "",
  onChange,
  className,
  shortcut = "⌘K",
}: SearchInputProps) {
  const [internalVal, setInternalVal] = useState(value);

  useEffect(() => {
    setInternalVal(value);
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInternalVal(e.target.value);
    onChange?.(e.target.value);
  };

  const handleClear = () => {
    setInternalVal("");
    onChange?.("");
  };

  return (
    <div className={cn("relative flex items-center w-full max-w-sm", className)}>
      <Search className="absolute left-3 w-4 h-4 text-slate-400 pointer-events-none" />
      <input
        type="text"
        value={internalVal}
        onChange={handleChange}
        placeholder={placeholder}
        className="w-full pl-9 pr-14 py-1.5 text-xs bg-white border border-slate-200 rounded text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all shadow-subtle"
      />
      {internalVal ? (
        <button
          onClick={handleClear}
          className="absolute right-2.5 p-0.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      ) : (
        shortcut && (
          <kbd className="absolute right-2 px-1.5 py-0.5 text-[10px] font-mono text-slate-400 bg-slate-50 border border-slate-200 rounded pointer-events-none">
            {shortcut}
          </kbd>
        )
      )}
    </div>
  );
}

interface FilterOption {
  label: string;
  value: string;
}

interface FilterDropdownProps {
  label?: string;
  options: FilterOption[];
  value: string;
  onChange: (val: string) => void;
  className?: string;
}

export function FilterDropdown({
  label,
  options,
  value,
  onChange,
  className,
}: FilterDropdownProps) {
  return (
    <div className={cn("flex items-center gap-1.5", className)}>
      {label && <span className="text-xs text-slate-500 font-medium whitespace-nowrap">{label}:</span>}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="text-xs bg-white border border-slate-200 rounded py-1.5 px-2.5 text-slate-700 hover:border-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all shadow-subtle cursor-pointer font-medium"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}

interface ExportMenuProps {
  onExportCsv: () => void;
  onExportJson?: () => void;
  label?: string;
  className?: string;
}

export function ExportMenu({ onExportCsv, onExportJson, label = "Export", className }: ExportMenuProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className={cn("relative inline-block text-left", className)}>
      <button
        onClick={() => setOpen(!open)}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded hover:bg-slate-50 shadow-subtle transition-colors"
      >
        <svg className="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        {label}
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-20" onClick={() => setOpen(false)} />
          <div className="absolute right-0 mt-1 w-36 bg-white border border-slate-200 rounded shadow-dropdown z-30 py-1 text-xs">
            <button
              onClick={() => {
                onExportCsv();
                setOpen(false);
              }}
              className="w-full text-left px-3 py-1.5 hover:bg-slate-50 text-slate-700 font-medium"
            >
              Export CSV
            </button>
            {onExportJson && (
              <button
                onClick={() => {
                  onExportJson();
                  setOpen(false);
                }}
                className="w-full text-left px-3 py-1.5 hover:bg-slate-50 text-slate-700 font-medium"
              >
                Export JSON
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
}
