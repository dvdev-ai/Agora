export function clamp(n: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, n));
}

export function average(nums: number[]): number {
  if (!nums.length) return 0;
  return nums.reduce((a, b) => a + b, 0) / nums.length;
}

export function formatScore(n: number): string {
  return Number.isInteger(n) ? String(n) : n.toFixed(1);
}

export function cn(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(" ");
}

export type IdeaAngle = {
  title: string;
  text: string;
};

/** Локальный генератор трех углов идеи без сервера — для демо на сайте. */
export function expandIdeaLocally(seed: string): IdeaAngle[] {
  const clean = seed.trim().replace(/\s+/g, " ");
  const short =
    clean.length > 90 ? `${clean.slice(0, 87).trim()}...` : clean || "пустая мысль";

  return [
    {
      title: "Реалистично",
      text:
        `Возьми ядро «${short}» и сделай минимальную версию на одну неделю: ` +
        `один канал, одна привычка, один измеримый результат. Без бренда и без сложной архитектуры. ` +
        `Критерий успеха — не идеал, а повторяемость: получилось ли вернуться к этому еще раз.`,
    },
    {
      title: "Смело",
      text:
        `Разверни ту же мысль как опыт, которым можно делиться: маленькое сообщество, ритуал, ` +
        `публичный эксперимент на 14 дней. Пусть «${short}» станет не продуктом, а сценой, ` +
        `где люди встречаются вокруг одного чувства или задачи. Риск выше — и ясность тоже.`,
    },
    {
      title: "Абсурдно",
      text:
        `Доведи идею до края: «${short}» как ночной спектакль, карта города по настроению, ` +
        `или переписка с будущим собой через год. Абсурд здесь не шутка ради шутки — ` +
        `он вытаскивает спрятанный голод: чего тебе на самом деле не хватает в исходной мысли.`,
    },
  ];
}

export type DemoCheckup = {
  id: string;
  createdAt: string;
  mood: number;
  anxiety: number;
  energy: number;
  sleep: number;
  note: string;
};

export function createCheckupId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function summarizeCheckups(items: DemoCheckup[]): {
  count: number;
  mood: number;
  anxiety: number;
  energy: number;
  sleep: number;
  trend: string;
} {
  if (!items.length) {
    return {
      count: 0,
      mood: 0,
      anxiety: 0,
      energy: 0,
      sleep: 0,
      trend: "Пока пусто — пройди первый чек-ап.",
    };
  }

  const mood = average(items.map((x) => x.mood));
  const anxiety = average(items.map((x) => x.anxiety));
  const energy = average(items.map((x) => x.energy));
  const sleep = average(items.map((x) => x.sleep));

  let trend = "Пока рано говорить о тренде — накопи еще пару точек.";
  if (items.length >= 3) {
    const mid = Math.floor(items.length / 2);
    const first = items.slice(0, mid);
    const second = items.slice(mid);
    const moodDelta = average(second.map((x) => x.mood)) - average(first.map((x) => x.mood));
    const anxietyDelta =
      average(second.map((x) => x.anxiety)) - average(first.map((x) => x.anxiety));
    const bits: string[] = [];
    if (moodDelta >= 0.7) bits.push("настроение чуть выше");
    if (moodDelta <= -0.7) bits.push("настроение просело");
    if (anxietyDelta >= 0.7) bits.push("тревога выросла");
    if (anxietyDelta <= -0.7) bits.push("тревога чуть отпустила");
    trend = bits.length ? `Тренд · ${bits.join(", ")}` : "Тренд ровный — без резких качелей.";
  }

  return {
    count: items.length,
    mood,
    anxiety,
    energy,
    sleep,
    trend,
  };
}
