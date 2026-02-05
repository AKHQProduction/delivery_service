export interface Phone {
  id?: number;
  number: string;
  is_primary: boolean;
}

export interface AddressCoordinates {
  latitude: number;
  longitude: number;
}

export interface Address {
  id?: number;
  street: string;
  house: string;
  apartment?: string;
  entrance?: string;
  floor?: string;
  intercom?: string;
  is_primary: boolean;
  comment?: string;
  coordinates?: AddressCoordinates | null;
}

export interface Client {
  client_id: string;
  full_name?: string;
  phones?: Phone[];
  addresses?: Address[];
}
