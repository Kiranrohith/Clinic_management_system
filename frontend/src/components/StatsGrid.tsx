type Stat = { label: string; value: number };

type Props = {
  stats: Stat[];
};

export function StatsGrid({ stats }: Props) {
  return (
    <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((item) => (
        <article key={item.label} className="rounded border bg-white p-4">
          <p className="text-sm text-slate-600">{item.label}</p>
          <p className="text-2xl font-semibold">{item.value}</p>
        </article>
      ))}
    </section>
  );
}
