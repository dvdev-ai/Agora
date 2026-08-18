import type { IdeaAngle } from "@/lib/utils";

const REALISTIC_OPENERS = [
  "Собери минимальную версию на семь дней",
  "Оставь только ядро и один измеримый результат",
  "Сделай черновик ритуала, а не продукт",
];

const BOLD_OPENERS = [
  "Разверни это как публичный эксперимент",
  "Собери маленькое сообщество вокруг чувства",
  "Преврати мысль в сцену, а не в задачу",
];

const ABSURD_OPENERS = [
  "Доведи до театрального края",
  "Сделай из этого ночную карту города",
  "Пусть идея пишет письма будущему тебе",
];

function pick<T>(arr: T[], seed: string, salt: number): T {
  let hash = salt;
  for (let i = 0; i < seed.length; i += 1) {
    hash = (hash * 33 + seed.charCodeAt(i)) % 100000;
  }
  return arr[Math.abs(hash) % arr.length];
}

function clip(seed: string, max = 88): string {
  const clean = seed.trim().replace(/\s+/g, " ");
  if (!clean) return "пустая мысль";
  return clean.length > max ? `${clean.slice(0, max - 3).trim()}...` : clean;
}

/**
 * Более вариативный локальный движок /idea для витрины.
 * Не заменяет модель в боте — только помогает почувствовать формат.
 */
export function expandIdeaRich(seed: string): IdeaAngle[] {
  const short = clip(seed);
  const realistic = pick(REALISTIC_OPENERS, short, 3);
  const bold = pick(BOLD_OPENERS, short, 7);
  const absurd = pick(ABSURD_OPENERS, short, 13);

  return [
    {
      title: "Реалистично",
      text:
        `${realistic}: возьми «${short}» и убери все украшения. ` +
        `Один канал, одна привычка, один признак что это живо. ` +
        `Если за неделю к мысли хочется вернуться — ядро настоящее. Если нет — ты увидел, что тянуло не к идее, а к ощущению рядом с ней.`,
    },
    {
      title: "Смело",
      text:
        `${bold}. Пусть «${short}» станет местом встречи: не обязательно приложение, иногда хватает ритуала и языка. ` +
        `Смелость тут не в масштабе инвестиций, а в готовности показать недоделанное и проверить, откликается ли это в других.`,
    },
    {
      title: "Абсурдно",
      text:
        `${absurd}. Представь, что «${short}» больше не обязана быть полезной — только честной. ` +
        `На этом краю обычно всплывает спрятанный голод: свободы, признания, тишины, игры. ` +
        `Абсурд нужен не чтобы шутить, а чтобы увидеть, чего исходной мысли не хватало для дыхания.`,
    },
  ];
}

export function describeIdeaMode(): string {
  return (
    "На сайте /idea работает как локальный эскиз. " +
    "В Telegram тот же жест делает живая модель: глубже, свободнее и ближе к твоему контексту."
  );
}
