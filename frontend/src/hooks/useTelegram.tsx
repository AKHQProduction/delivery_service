import { useEffect, useState } from "react";
import initDataTG from "../services/tgInitData";

export const useTelegram = () => {
  const [isTGWebApp, setIsTGWebApp] = useState(false);

  useEffect(() => {
    const tg = initDataTG;
    if (tg) {
      setIsTGWebApp(true); // eslint-disable-line react-hooks/set-state-in-effect -- one-time init
      if (tg.ready) {
        tg.ready();
      }
    }
  }, []);

  return { isTGWebApp, initDataTG };
};
