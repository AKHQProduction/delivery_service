# Client Preferred Delivery Time Design

## Goal

Operators currently must choose "Час доставки" manually for every new order. Add an optional preferred delivery time slot to the client card so the new order form can preselect the client's usual slot.

## Scope

This feature is only a UI convenience for creating orders. It does not change order creation rules: the order API still receives an explicit `time_slot_id`, and the operator can override the preselected value before saving.

In scope:

- Store an optional preferred time slot on each client.
- Show and edit the preference in add/edit client forms.
- Return the preference from client read endpoints and list endpoints.
- Preselect the preferred slot in new order forms after a client is selected.
- Keep existing orders unchanged.

Out of scope:

- Automatically changing existing or future orders on the backend.
- Inferring preferences from previous orders.
- Per-address or per-phone delivery time preferences.
- Applying the preference while editing an existing order.

## Data Model

Add `clients.preferred_time_slot_id` as a nullable UUID foreign key to `shop_delivery_time_slots.id`.

The foreign key uses `ON DELETE SET NULL`, so deleting a time slot clears affected client preferences without deleting clients.

Old clients are migrated with `preferred_time_slot_id = NULL`.

## Backend API

Client create and edit payloads accept optional `preferred_time_slot_id`.

Client read models include `preferred_time_slot_id` so both client lists and individual client reads can drive the order form.

Validation rules:

- `null` or omitted means no preferred slot.
- A provided slot must exist.
- A provided slot must belong to the same shop as the client.
- A slot from another shop is rejected with the existing access/validation error style used in the backend.

Order create and edit APIs are not changed. They continue to require or accept `time_slot_id` explicitly.

## Frontend

The `Client` type gains `preferred_time_slot_id?: string | null`.

Add and edit client forms show an optional select labelled `Бажаний час доставки`. Options come from the existing `useTimeSlotsSettings()` hook and use the same label formatting as order forms.

When creating an order:

- Selecting a client sets phone and address as today.
- If the selected client has `preferred_time_slot_id`, `useOrderForm` sets `formData.timeSlotId` to that value.
- If there is no preference, the time slot remains empty.
- If the operator manually changes the slot, that explicit value is submitted.
- Editing an existing order ignores the client preference and keeps the order's current `time_slot_id`.

## Error Handling

If a client preference points to a deleted slot, the database clears it through `ON DELETE SET NULL`; the UI sees no preference.

If a stale frontend sends a non-existent or foreign-shop slot, the backend rejects the create/edit client request and leaves the client unchanged.

If the time slot list fails to load in the client form, the preference select renders with no selectable slots and the rest of the client form remains usable.

## Testing

Backend tests cover:

- Creating a client with `preferred_time_slot_id` persists and returns it.
- Editing a client can set, change, and clear `preferred_time_slot_id`.
- Reading client lists includes `preferred_time_slot_id`.
- A slot from another shop cannot be assigned to a client.
- Deleting a time slot clears the client's preference.

Frontend verification covers:

- TypeScript build passes.
- Lint passes, or any existing unrelated lint failures are documented.
- New order form preselects the preferred slot when a client is selected.
- New order form leaves the slot empty for clients without a preference.
