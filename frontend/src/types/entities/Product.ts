export interface Product {
  product_id: string;
  name: string;
  category_id: string;
  category_name?: string;
  price: number;
}

export interface transformedCategories {
  id: string;
  name: string;
  emoji: string;
}