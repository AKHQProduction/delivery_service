export const hasLetter = (s: string) => /[a-zA-Zа-яА-ЯіІїЇєЄґҐёЁ]/.test(s);
export const hasDigit = (s: string) => /\d/.test(s);