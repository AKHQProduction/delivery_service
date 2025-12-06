import { useState } from "react";

const clientsData = {
  clients: [
    {
      client_id: "БИДЛ001",
      full_name: "Іван Петренко",
      number: ["+380501234567"],
      address: ["вул. Шевченка який пасе ягнят за селом, 10, Київ"],
    },
    {
      client_id: "БИДЛ002",
      full_name: "Олена Ковальчук",
      number: ["+380671112233", "+380631112234"],
      address: ["просп. ТЦК, 5, Львів", "вул. Грушевського, 20, Львів"],
    },
    {
      client_id: "БИДЛ003",
      full_name: "Петро Іванов",
      number: ["+380931234567"],
      address: ["вул. Пушкіна Гандона, 15, Одеса"],
    },
  ],
};

export const useClient = () => {
  const [clients, setClients] = useState(clientsData.clients);

  return { clients };
};
