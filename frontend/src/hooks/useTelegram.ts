import { useEffect, useState } from "react";
import initDataTG from "../services/tgInitData";

export const useTelegram = () => {
  const [isTGWebApp, setIsTGWebApp] = useState(false);

  useEffect(() => {
    const tg = initDataTG;
    if (tg) {
      setIsTGWebApp(true);
      tg.ready();
    }
  }, []);

  return { isTGWebApp, initDataTG };
};
