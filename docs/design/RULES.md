# Water Delivery Design Rules

## Purpose

This document defines the visual redesign direction for Water Delivery, an internal B2B operations system for water delivery management.

Water Delivery is a daily-use admin, CRM, and logistics tool for owners, managers, and couriers. The interface must prioritize speed, scanning, accuracy, and repeated operational work.

The product must feel like a serious internal operations system, not a marketing website, consumer ecommerce app, or decorative concept.

## Design Direction

Use an IBM Carbon-inspired enterprise operations foundation:

- Structured, reliable, precise, accessible, and professional.
- Form-heavy and table-friendly.
- Clear navigation, clear page structure, and predictable actions.
- Compact controls, muted surfaces, thin borders, and strong alignment.

Combine it with Airtable-like structured data clarity:

- Entity management screens should feel like clean database views.
- Products, clients, orders, staff, and settings must be easy to search, filter, scan, compare, and edit.
- Use tables, category chips where relevant, selected rows, side detail panels, pagination, and row actions.

For routes and maps, use practical mobility clarity:

- Stops must be numbered and easy to distinguish.
- Route order, delivery time slots, warnings, and correction actions must be obvious.
- Maps should be operational and readable, with strong contrast for route lines and markers.

Do not copy IBM, Airtable, Uber, or any other brand literally.

## Visual System

### Typography

- Use Inter.
- Use compact but readable type sizes.
- Page titles should be strong and clear.
- Table text, labels, helper text, metadata, and captions should be smaller but legible.
- Avoid oversized marketing-style headings.
- Do not use negative letter spacing.

Recommended type scale:

- Page title: 24px / 32px.
- Section title: 16px / 24px.
- Body and table text: 14px / 20px.
- Metadata, captions, helper text: 12px / 16px.
- Buttons and compact controls: 14px / 20px.

### Color Palette

- Background: `#F8FAFC`.
- Surface: `#FFFFFF`.
- Surface muted: `#F1F5F9`.
- Text: `#0F172A`.
- Muted text: `#64748B`.
- Border: `#E2E8F0`.
- Primary: `#0F62FE`.
- Primary hover: `#0043CE`.
- Primary muted: `#DBEAFE`.
- Secondary/link: `#2563EB`.
- Success: `#22C55E`.
- Warning: `#F59E0B`.
- Error: `#EF4444`.
- Focus ring: `#2563EB`.

Color must communicate action, status, or hierarchy. Avoid one-note palettes and decorative color usage.

### Shape and Elevation

- Use 6-8px border radius for cards, panels, modals, controls, and table containers.
- Use 1px borders for inputs, panels, tables, and cards.
- Use subtle shadows only for modals, popovers, and elevated panels.
- Avoid nested cards.
- Avoid decorative sections, floating marketing cards, gradient backgrounds, blobs, bokeh, and glassmorphism.

### Icons

- Use clean SVG-style line icons.
- Use icons only when they improve scanning or clarify an action.
- Do not use emoji icons.
- Do not use decorative illustrations.

## Layout Rules

### Desktop Shell

- Use a fixed left sidebar.
- Use a top page header with title, short context, search, filters, and primary actions.
- Keep primary actions visible and predictable.
- Main content should use dense tables, summary cards, panels, and task-focused modals.
- Use right-side detail panels for entity inspection when useful.
- Use centered or right-side modals for create/edit flows depending on complexity.

Desktop sidebar labels:

- Water Delivery
- Головна
- Товари
- Клієнти
- Замовлення
- Маршрути
- Персонал
- Налаштування магазину

`Статистика` is not a separate navigation item. Home combines dashboard and statistics.

`Налаштування` is not a separate product navigation item. Telegram-specific display settings are outside the main system mockups.

### Mobile Shell

- Use bottom navigation for frequent sections: `Головна`, `Товари`, `Клієнти`, `Замовлення`.
- Use a top-left menu button to open a slide-out drawer/sidebar for the full navigation.
- The mobile drawer shows: `Water Delivery`, `Головна`, `Товари`, `Клієнти`, `Замовлення`, `Маршрути`, `Персонал`, `Налаштування магазину`.
- Do not include `Статистика` or separate `Налаштування` in mobile navigation.

### Data Screens

Entity list screens should include:

- Page title.
- Search input.
- Filters or filter chips.
- Primary create action.
- Dense table or structured record list.
- Row selection where bulk or detail actions exist.
- Row action menu.
- Status pills.
- Pagination when lists are long.
- Side detail panel for selected records when useful.

Decision rules:

- Use a side detail panel for quick record inspection and lightweight contextual actions.
- Use a centered modal for short create/edit tasks with few fields.
- Use a right-side drawer or full-height panel for complex edit flows that need context from the list.
- Use a full page form only for long workflows such as order creation, import mapping, or route editing.
- Keep destructive actions behind a confirmation modal.

### Forms and Modals

Forms should be compact, grouped, and task-focused:

- Always show labels.
- Mark required fields.
- Show validation messages directly under fields.
- Use clear primary and secondary actions.
- Disable submit buttons only when the reason is clear.
- Show destructive confirmation before deleting records.

Modals should not become decorative boards. They should represent a clear task:

- Add product: `Додати товар`.
- Edit product: `Редагувати товар`.
- Add client: `Додати клієнта`.
- Edit client: `Редагувати клієнта`.
- Add order: `Додати замовлення`.
- Edit order: `Редагувати замовлення`.
- Export PDF: `Експорт PDF`.
- Invite employee: `Запросити працівника`.
- Copy invite link: `Скопіювати посилання`.
- Confirm deletion: `Підтвердити видалення`.

## Component Rules

### Tables

Tables should support:

- Search.
- Filters.
- Sort indicators when relevant.
- Row selection.
- Compact row actions.
- Status pills.
- Pagination.
- Empty states.
- Skeleton loading.

Tables must be readable and scan-friendly. Avoid overly tall rows.

Table density rules:

- Use compact rows around 44-48px high.
- Keep column headers sticky when the table scrolls vertically.
- Keep row actions visually compact and aligned to the right.
- Use horizontal overflow for wide operational tables instead of wrapping dense columns.
- Prefer truncation with tooltips for long names, addresses, comments, and metadata.
- Show sort direction only on sortable columns.

### Cards and Panels

Use cards for:

- Summary metrics.
- Independent repeated route cards.
- Side detail panels.
- Settings sections.
- Modal content.

Do not use cards as decorative page sections. Do not put cards inside cards unless the inner card is a functional repeated item.

### Payment Methods

Payment methods are user-defined and must not use guessed icons.

- Show payment method names as text.
- Use neutral bars, amounts, and percentages for breakdowns.
- Do not assign icons to `Готівка`, `На рахунок`, `Баланс`, or custom payment methods.

### Status and Labels

Do not invent workflow statuses that are not tracked by the system.

- Products do not have active/inactive status.
- Clients do not have permanent/new labels.
- Orders do not have delivery workflow statuses such as delivered, planned, canceled, or postponed.
- Routes do not have statuses. Routes are generated from orders grouped by delivery date and time slot.
- Orders without coordinates are still included in routes and placed at the end of the stop list.

Use status-like visual treatment only for real system states such as validation errors, destructive confirmations, import results, or missing coordinates warnings.

### Toasts and Alerts

Toasts should be small, clear, and consistently positioned.

Required states:

- Success toast: `Замовлення створено`.
- Error toast: `Не вдалося зберегти зміни`.
- Duplicate phone warning: `Клієнт з таким телефоном вже існує`.
- Missing coordinates warning: `3 замовлення без координат. Вони додані в кінець маршруту.`

### Loading and Empty States

Use skeletons for tables and record lists.

Use compact spinners only for short blocking actions.

Empty states must be practical:

- No decorative illustration.
- One short message.
- One clear next action when relevant.

Example:

- `Немає замовлень`.
- Button: `Створити замовлення`.

### Interaction Rules

- Every interactive control must have visible hover, focus, active, disabled, and loading states.
- Keyboard focus must be visible on buttons, inputs, links, menus, tabs, table rows, and map correction controls.
- Selected rows and selected filters must be visually distinct without relying only on color.
- Disabled controls should include nearby helper text or validation text when the reason is not obvious.
- Dirty forms should warn before closing or navigating away.
- Destructive actions must use explicit confirmation copy and a clearly destructive action style.

## Product Scope

The redesign must reflect these product capabilities:

- Login via Telegram.
- Create shop.
- Main dashboard.
- Products management.
- Categories management.
- Clients management.
- Add/edit client with phones and addresses.
- Duplicate phone warning.
- Excel client import flow.
- Orders list.
- Add/edit order.
- Order detail.
- Pay order from client balance.
- PDF document export.
- Home dashboard with order statistics.
- Routes list by delivery date.
- Route detail with stops list and map.
- Set/update order coordinates through map picker.
- Staff list.
- Invite employee flow.
- Shop settings: address, districts, time slots, payment methods.
- Toasts, loading, empty, validation, disabled, and error states.

## Core Entities

### Products

- Name.
- Price.
- Category.

Do not add inventory, SKU, warehouse, active/inactive status, duplicate product action, or product image functionality unless explicitly requested.

### Clients

- Full name.
- Phones.
- Addresses.
- Balance.

Client screens should make duplicate phones, debt, and address management easy to notice.

### Orders

- Client.
- Products and quantities.
- Delivery phone.
- Delivery address.
- Delivery date.
- Time slot.
- Payment method.
- Payment status.
- Comment/note.
- Total amount.

Orders should be easy to browse by date and payment method. Do not add delivery workflow statuses unless the system starts tracking them.

### Routes

- Delivery date.
- Time slot.
- Route stops.
- Order/client/address per stop.
- Orders without coordinates.
- Map marker correction.

Route screens should make stop order and coordinate problems obvious.

### Staff

- Full name.
- Role: OWNER, MANAGER, COURIER.
- Invite link.

Staff screens should clearly separate existing employees, pending invites, role changes, and invite link sharing.

## Screen Groups

Generate or design screenshots by flow, not as one giant board.

### 1. Auth and Onboarding

- Login via Telegram.
- Login error state.
- Create shop form.
- Create shop error state.

### 2. Navigation and Main Dashboard

- Desktop shell with sidebar.
- Home as combined dashboard and statistics.
- Date range selector.
- Total orders.
- Total sum.
- Product count in orders.
- Average order value.
- Payment method breakdown without icons.
- Category breakdown.
- Time slot breakdown.
- Recent orders.

### 3. Products Flow

- Products list.
- Empty products state.
- Product search.
- Add product modal.
- Edit product modal.
- Category management modal.

### 4. Clients Flow

- Clients list.
- Client search.
- Add client form.
- Edit client form.
- Duplicate phone warning.
- Import Excel upload step.
- Import column mapping step.
- Import result step.

### 5. Orders Flow

- Orders list.
- Date filters.
- Export PDF modal.
- Add order form.
- Order detail modal.
- Edit order form.
- Pay from balance action/error state.

### 6. Statistics Flow

Standalone statistics is deprecated. Statistics belong on `Головна`.

### 7. Routes Flow

- Routes list by date.
- Route plan cards by time slot.
- Orders without coordinates warning.
- Route detail with stops list and map.
- Reorder/reverse route controls.
- Marker edit mode.
- Map picker for setting coordinates.

### 8. Staff and Settings Flow

- Staff list.
- Add/invite employee modal.
- Invite link modal.
- Edit employee modal.
- Shop settings with internal categories.
- Profile settings.
- Address and geography settings.
- Districts settings.
- Time slots settings.
- Payment methods settings without icons.
- PDF document settings.
- Excel import settings.

### 9. System States

- Success toast.
- Error toast.
- Loading spinner.
- Skeleton loading.
- Empty state.
- Validation error.
- Disabled button state.
- Destructive confirmation state.

## Content Rules

- Ukrainian UI labels must be rendered verbatim where specified.
- Use concise operational labels.
- Avoid marketing copy.
- Avoid explanatory feature text inside the app unless it is needed for an empty state, warning, validation message, or onboarding step.
- Keep actions direct and predictable.

## Explicit Constraints

Do not include:

- Product images or thumbnails.
- Decorative hero sections.
- Landing page composition.
- Marketing copy.
- Fake ecommerce features.
- Inventory, SKU, or warehouse functionality unless explicitly requested.
- Delivery tracking, chat, or courier live location unless explicitly requested.
- Gradients.
- Glassmorphism.
- Blobs.
- Bokeh.
- Decorative illustrations.
- Purple AI-style palette.
- Emoji icons.

## Output Standard

Each generated or implemented screen must:

- Look like a real production app screenshot.
- Represent one screen group clearly.
- Keep functionality faithful to the existing system.
- Use the established app shell and layout scope consistently.
- Preserve dense but comfortable spacing.
- Keep text readable.
- Use clear hierarchy and predictable controls.
