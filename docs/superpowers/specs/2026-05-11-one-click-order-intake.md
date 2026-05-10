# PRD: One-Click Order Intake From Last Client Order

## Problem Statement

Managers create many orders for returning water delivery clients. Today the
main Order intake flow requires selecting a client, selecting products,
choosing contact data, choosing delivery date and slot, selecting payment, and
then creating the order.

For repeat clients this is slower than necessary because the manager usually
wants to repeat the client's most recent order with small or no changes. The
current product also exposes repeat-order behavior from client history contexts,
but that is not where managers naturally start when they are creating orders.

The problem from the manager's perspective: while creating a new order from the
Orders page, the system does not proactively offer to reuse the last known
client order after the client is selected.

## Solution

Add a one-click repeat suggestion inside the main Orders page order creation
flow.

When the manager opens `Нове замовлення` and selects a client, the frontend
looks up that client's most recent order. If the new order form is still clean
and a repeatable last order exists, the app shows a compact confirmation modal:
`Повторити останнє замовлення?`

The manager can reject the suggestion and continue manually, or confirm it. On
confirm, the app fills the current order form using the last order where safe:
products and quantities from the last order, payment method and comment from
the last order, delivery date as tomorrow, contact data matched from the client
record, and delivery slot from the selected address preferred time slot.

The confirmation does not create the order. It only applies the draft to the
form. The manager still reviews the form and uses the normal
`Створити замовлення` action.

## User Stories

1. As a manager, I want the repeat-order prompt to appear inside `Нове замовлення`, so that I can create repeat orders from the same place where I create all other orders.
2. As a manager, I want the prompt to appear after I select a client, so that the system can use the selected client's history.
3. As a manager, I want the prompt to use only the client's latest order, so that the flow remains quick and does not become a history picker.
4. As a manager, I want no prompt when the selected client has no previous orders, so that the normal order form stays quiet.
5. As a manager, I want no prompt when the latest order has no currently available products, so that I am not offered an unusable repeat.
6. As a manager, I want the prompt only when the order form is still clean, so that my manually entered products, payment, note, date, or time are not overwritten.
7. As a manager, I want the prompt not to reappear for a client I rejected during the same form session, so that I am not interrupted repeatedly.
8. As a manager, I want the prompt to appear again after closing and reopening `Нове замовлення`, so that a previous rejection does not persist longer than the current task.
9. As a manager, I want the prompt to show the previous order date and time, so that I understand which order will be reused.
10. As a manager, I want the prompt to show product names and quantities, so that I can quickly verify the repeated contents.
11. As a manager, I want the prompt to show the previous order total, so that I can compare expected value before applying it.
12. As a manager, I want the prompt to show the payment method, so that I know what will be copied to the form.
13. As a manager, I want the prompt to show the previous comment when present, so that I can decide whether it is still relevant.
14. As a manager, I want `Відхилити` to close the prompt and keep the selected client, so that I can continue building the order manually.
15. As a manager, I want `Підтвердити` to fill the form but not create the order, so that I can review or adjust it before saving.
16. As a manager, I want the delivery date to default to tomorrow when applying the last order, so that repeat orders target the next delivery day by default.
17. As a manager, I want the delivery slot to come from the selected address preferred time slot, so that the draft follows the client's current delivery preference.
18. As a manager, I want the delivery slot to remain empty when the selected address has no preferred time slot, so that the system does not guess a random slot.
19. As a manager, I want the phone to be matched from the previous order phone number when possible, so that repeat orders preserve the client's last used contact.
20. As a manager, I want the phone to fall back to the primary or first client phone when matching fails, so that the draft can still move forward.
21. As a manager, I want the address to be matched from the previous order address when possible, so that repeat orders preserve the last used delivery destination.
22. As a manager, I want the address to fall back to the primary or first client address when matching fails, so that the draft can still move forward.
23. As a manager, I want only currently available products to be copied, so that the form does not contain invalid product references.
24. As a manager, I want a warning toast if some products from the last order are unavailable, so that I know the repeated order is incomplete.
25. As a manager, I want a warning toast if required fields remain missing after applying the draft, so that I know what must be completed before creation.
26. As a manager, I want a success toast after the last order is applied cleanly, so that I have clear feedback that the action worked.
27. As a manager, I want the normal create button validation to remain in place, so that invalid orders cannot be submitted.
28. As a manager, I want the existing manual order form to remain available, so that unusual orders are still handled without a separate path.
29. As a manager, I want this feature not to add shortcuts to the Client page or client side panel, so that order creation behavior stays concentrated in the Orders page.
30. As a manager, I want the existing recent-order sections to remain informational or planning-oriented, so that the new one-click flow has one clear primary entry point.

## Implementation Decisions

- The feature belongs to the frontend Order intake flow, not to the client detail side panel or recent-order history actions.
- The trigger is client selection inside the new order form opened from the Orders page.
- The repeat suggestion is scoped to one client and one form session.
- The frontend should fetch the selected client's latest recent order after client selection.
- The frontend should show no UI when the selected client has no previous orders.
- The frontend should show no UI when the latest order cannot contribute at least one currently available product.
- The frontend should not show the prompt if the form is no longer clean.
- A clean form means no selected products, no manually selected payment method, no comment, and no user-changed delivery date or delivery slot beyond the default state.
- Rejecting the prompt stores the rejected client id in local component state for the current form instance only.
- Confirming the prompt applies a draft to the existing new order form; it does not call order creation.
- The applied draft uses tomorrow as the delivery date.
- The applied draft uses the selected address preferred time slot as `time_slot_id`.
- If the selected address has no preferred time slot, `time_slot_id` remains empty and the existing form validation blocks creation until the manager chooses a slot.
- Phone selection first tries to match the previous order delivery phone against the selected client's phones by number.
- If phone matching fails, phone selection falls back to the client's primary phone or first phone.
- Address selection first tries to match the previous order delivery address against the selected client's addresses by street, house, and apartment.
- If address matching fails, address selection falls back to the client's primary address or first address.
- Products are matched by `product_id` against currently available products loaded by the order form.
- Products without a current product match are skipped.
- If at least one product is skipped, show warning toast `Деякі товари з останнього замовлення недоступні`.
- If any required field remains missing after applying the draft, show warning toast `Заповніть відсутні поля перед створенням`.
- If the draft applies without product skips and without missing required fields, show success toast `Останнє замовлення застосовано`.
- Toasts should use the app's existing global toast mechanism instead of introducing a new form-local toast container.
- The confirmation modal is read-only; it does not include inline editing.
- The confirmation modal shows the previous order date and time, product names and quantities, total amount, payment method, and comment when present.
- The confirmation modal actions are `Відхилити` and `Підтвердити`.
- The existing `Створити замовлення` button remains the only action that creates the order.
- The implementation should prefer extracting repeat-draft decision logic into a small, testable module rather than burying matching and validation rules inside the form component.
- The repeat-draft module should expose an intent-level interface: given a client, latest order, available products, current date, and payment method availability, return either no suggestion or an applicable draft plus warnings.
- The form component should own UI state: prompt visibility, rejected client ids for the current session, and calling form field mutation handlers.
- The data access layer can reuse the existing recent orders read path if it continues to provide enough data for the prompt and draft.
- If current order read data does not include stable ids for phone, address, or time slot, the first implementation should use matching and fallback rules rather than requiring a backend schema change.

## Testing Decisions

- Tests should cover externally visible behavior and product decisions rather than internal React state names.
- The repeat-draft module should have focused unit tests because it contains the deepest logic: product matching, phone matching, address matching, preferred time slot selection, missing-required-field detection, and warning production.
- The new order form should have integration or component tests around user behavior: selecting a client with a latest order shows the prompt, rejecting suppresses it for the current form session, confirming fills the form, and the form still requires missing fields before creation.
- Tests should verify that no prompt appears when the client has no recent orders.
- Tests should verify that no prompt appears when no products from the latest order can be matched.
- Tests should verify that partial product matches apply available products and surface the unavailable-products warning.
- Tests should verify that the delivery date becomes tomorrow according to the app's current Kyiv business date boundary.
- Tests should verify that the delivery slot comes from the selected address preferred time slot and remains empty when no preferred slot exists.
- Tests should verify that phone matching prefers the previous order phone number before falling back to primary or first phone.
- Tests should verify that address matching prefers the previous order address before falling back to primary or first address.
- Tests should verify that confirming the prompt does not create an order until the manager clicks `Створити замовлення`.
- Existing frontend order form tests, if present, should be extended rather than replacing the current manual creation coverage.
- Backend tests are not required for the first version unless the implementation changes the order read model or recent-order API contract.

## Out of Scope

- Creating an order immediately from the confirmation modal.
- Showing a list of the last 3-5 orders.
- Adding one-click order shortcuts to the Client page, client side panel, or recent-order cards.
- Changing regular order template creation or planning behavior.
- Persisting rejected suggestions across browser sessions.
- Creating a new backend endpoint solely for one-click order intake.
- Changing product availability rules.
- Changing payment method configuration behavior.
- Automatically guessing a delivery slot when the selected address has no preferred time slot.
- Editing products, payment, date, or comments inside the confirmation modal.

## Further Notes

- This feature should use the existing Order intake language: client, delivery slot, address, phone, product list, payment method, comment, and persisted Order.
- The UX goal is to speed up the common repeat-client order path without creating a second order creation surface.
- The modal is an acceleration aid, not a bypass around the current order form validation.
- The implementation should be careful not to overwrite manager-entered form data.
- Future backend work could expose phone id, address id, and time slot id on recent order read models, but the first version can proceed with matching and fallback rules.
