export interface Phone {
  id?: number;
  number: string;
  is_primary: boolean;
}

export interface Address {
  id?: number;
  street: string;
  house: string;
  address_type: "APARTMENT" | "PRIVATE_HOUSE";
  apartment?: string;
  entrance?: string;
  floor?: string;
  intercom?: string;
  is_primary: boolean;
}

export interface Client {
  client_id: string;
  full_name?: string;
  custom_id?: string;
  phones?: Phone[];
  addresses?: Address[];
}