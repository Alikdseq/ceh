"use client";

import { useRouter } from "next/navigation";
import { Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface SearchFormProps {
  className?: string;
  placeholder?: string;
}

export function SearchForm({ className, placeholder = "Поиск по артикулу или серии…" }: SearchFormProps) {
  const router = useRouter();

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const q = new FormData(form).get("q")?.toString().trim();
    if (q) router.push(`/search?q=${encodeURIComponent(q)}`);
  }

  return (
    <form onSubmit={handleSubmit} className={className} role="search">
      <div className="relative flex items-center">
        <Search className="pointer-events-none absolute left-3 h-4 w-4 text-muted-foreground" aria-hidden />
        <Input
          name="q"
          type="search"
          placeholder={placeholder}
          className="h-9 w-full pl-9 pr-20 bg-white/10 border-white/20 text-white placeholder:text-white/60 focus-visible:bg-white focus-visible:text-foreground focus-visible:placeholder:text-muted-foreground md:w-56 lg:w-64"
          aria-label="Поиск по каталогу"
        />
        <Button
          type="submit"
          size="sm"
          variant="ghost"
          className="absolute right-1 h-7 text-white hover:bg-white/20 hover:text-white focus-visible:text-white md:hidden"
        >
          Найти
        </Button>
      </div>
    </form>
  );
}
