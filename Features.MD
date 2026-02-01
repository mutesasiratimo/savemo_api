## Save Mo Finance – Feature Specification

### 1. System Overview
Save Mo Finance is a group- and individual-savings management platform with built‑in wallets, flexible saving goals, loans, and rich governance workflows.  
It is designed for Savings Groups, Investment Clubs, Cooperatives, SACCOs, and individuals who want structured saving, automated collections, and transparent portfolio tracking.

---

### 2. Authentication & User Management

#### 2.1 Identity & Accounts
- **User Accounts**: Phone/email-based accounts with secure password authentication.
- **Multi-Factor Authentication (optional)**: Support for OTP via SMS/email and/or TOTP apps.
- **Device Tracking**: Track login devices (browser, OS, IP, user agent) for security notifications.
- **KYC Profile (optional)**:
  - Basic: Name, contact, address, ID type & number.
  - Extended: Next of kin, occupation, employer, risk profile.

#### 2.2 Role & Permission Model (ACLs)
- **ACL-based Authorization**:
  - No fixed, hard-coded business roles like “Supervisor”, “Field Officer”, etc.
  - Instead we define **permissions** (ACL entries) such as:
    - `group.manage_members`
    - `group.manage_goals`
    - `group.approve_loans`
    - `wallet.view`
    - `wallet.debit`
    - `wallet.credit`
    - `finance.manage_invoices`
    - `events.manage`
    - `notifications.configure`
    - `system.admin`
  - Permissions are **defined in code** and attached to **role objects**.
- **Configurable Roles**:
  - System ships with default roles (e.g. `PlatformAdmin`, `GroupAdmin`, `Treasurer`, `Member`, `Auditor`), but these are just named sets of permissions.
  - Organizations can create custom roles by combining permissions.
- **User–Role Assignment**:
  - A user can have multiple roles **per context**:
    - Platform-level roles (e.g. platform admin).
    - Group-level roles (e.g. chairperson in Group A, treasurer in Group B).
  - Role assignments may have **start/end dates** to support time‑bound leadership.

#### 2.3 Session, Security & Password Management
- **Session Management**:
  - JWT or session tokens with configurable expiry.
  - Refresh tokens/rotating tokens for long-lived sessions.
- **Password Management**:
  - Strong password policies (configurable).
  - Password reset via email/SMS.
  - Audit trail for password changes and recovery attempts.
- **Security Events**:
  - Track sign-in/log-out, failed logins, password changes, device changes.
  - Trigger notifications (see Notifications Module).

---

### 3. Groups, Membership & Governance

#### 3.1 Group Structure
- **Groups**:
  - Logical container for users who save together (e.g. Savings Group, Investment Club).
  - Attributes: name, code, description, creation date, status (active, dormant, closed).
  - Optional metadata: location, meeting day/time, bank account mapping.
- **Parent/Child Groups**:
  - Groups can have **sub-groups** (hierarchical structure).
  - Use cases:
    - Large group with cells/chapters.
    - Committee subgroups (e.g. loans committee, welfare sub-group).
  - Parent-level goals can apply to all subgroups.

#### 3.2 Membership
- **Member Management**:
  - Add/remove users to groups.
  - Membership attributes: join date, exit date, status (pending, active, suspended, exited).
  - Per-group role assignments (chairperson, treasurer, secretary, etc.) implemented using ACL roles.
- **Leadership Positions**:
  - Define **positions** (e.g. Chairperson, Treasurer, Secretary, Loans Committee Member).
  - Each position:
    - Is mapped to one or more roles/ACL sets.
    - Has **tenure window**: start date and end date.
    - Can be renewed/rotated.
  - Supports overlapping leadership roles (e.g. Treasurer also in Loan Committee).

#### 3.3 Governance & Approvals
- **Approval Workflows** (configurable per group):
  - Loans approvals (multi-party).
  - Large withdrawals/refunds.
  - Changes to group saving goals.
  - Member onboarding/termination.
- **Committees**:
  - Define committees within groups (e.g. Loans Committee, Welfare Committee).
  - Each committee has:
    - Member list.
    - Required number of approvals or quorum rules for specific actions.

---

### 4. Savings Goals & Contributions

#### 4.1 Group Saving Goals
- **Goal Definition**:
  - Name, description.
  - Total target amount.
  - Target date or duration.
  - Currency.
  - Goal status: planned, active, paused, completed, cancelled.
- **Amortized Contributions**:
  - Define contribution rule by **amount + frequency**, e.g.:
    - “Each member pays 50,000 every month.”
    - “Each member pays 10,000 every week.”
  - Supported frequencies: daily, weekly, bi-weekly, monthly, quarterly, yearly, custom (N days).
  - Contributions **apply to all members** of the group and, optionally, its subgroups:
    - Each member has an individual schedule generated from the group rule.
  - Support multiple active group goals concurrently; a member’s obligations are aggregated across goals.

#### 4.2 Subgroups & Goal Inheritance
- **Inheritance Rules**:
  - Parent group goal can be:
    - Inherited by all subgroups (default).
    - Overridden at subgroup level (custom amount/frequency).
  - Subgroups can define **their own additional goals**.
- **Per-Member Obligations**:
  - A user who belongs to multiple groups/subgroups may have several obligations:
    - Per-group per-goal effective payment schedule is tracked.
  - System consolidates a user’s obligations into a unified **“My Obligations”** view.

#### 4.3 Individual Saving Goals
- **Personal Goals**:
  - Any user can create personal saving goals, independent of group goals.
  - Same properties as group goals: target amount, frequency, target date, etc.
- **Multiple Concurrent Goals**:
  - Support multiple personal goals with independent schedules.
  - Show aggregated view of:
    - Required contribution per period (sum over goals).
    - Actual paid vs expected.
- **Goal Adjustments**:
  - If a user is ahead of schedule or close to completion:
    - Allow bringing forward the goal completion date.
    - Adjust amortization going forward (lower per-period contribution or fewer periods).
  - Partial goal changes logged with full audit trail.

---

### 5. Wallets, Portfolios & Accounts

#### 5.1 Wallet Model
- **Wallet Types**:
  - **Individual Wallet**: For each user.
  - **Group Wallet**: For each group/subgroup.
  - Optional **Pooled Wallets**: E.g. product-specific or fund-specific pools.
- **Wallet Features**:
  - Balance tracking.
  - Transaction history (credits, debits, holds).
  - Support for multiple currencies (if needed).
  - Optional wallet-level limits (min/max balance, daily debit/credit limits).

#### 5.2 Portfolios
- **Portfolio View**:
  - Show consolidated view per user:
    - Wallet balance(s).
    - Active saving goals (group + personal).
    - Loan positions (borrowed vs repaid).
    - Investment products (if any future extension).
  - Show group-level portfolio:
    - Total member balances.
    - Total outstanding loans (to/from group).
    - Goal funding progress (per goal, aggregate).

#### 5.3 Invoices & Obligations
- **Invoice Generation**:
  - For each due period, the system can generate:
    - **Invoice per goal per member**, or
    - Consolidated **period invoice** per user (“You owe 500,000 this month”).
  - Invoices can be:
    - Paid directly (cashless/bank/cash).
    - Settled automatically from wallet balance.
- **Invoice Lifecycle**:
  - Status: pending, partially paid, paid, overdue, written-off.
  - Support surcharges/penalties for overdue invoices (configurable at group level).

---

### 6. Payments & Collections

#### 6.1 Payment Channels
- **Cashless / Mobile Money**:
  - Integration with mobile money providers (e.g. MTN, Airtel, etc.).
  - STK push or payment code-based flows.
- **Bank Transfers**:
  - Bank transfer instructions (virtual account or reference).
  - Webhooks or reconciliation feeds for incoming transfers.
- **Cash Payments**:
  - Manual capture of cash deposits by authorized roles (e.g. treasurer).
  - Attach evidence (receipt number, photo, reference).

#### 6.2 Payment Behaviors
- **Direct Invoice Payment**:
  - User pays specific invoice (e.g. “500,000 is due this month”).
  - Payment fully/partially clears that invoice.
- **Wallet Top-ups**:
  - User tops up wallet (no invoice targeting).
  - On due date(s), system auto-deducts from wallet to settle invoices.
- **Paying More Than Required**:
  - When a user pays above the expected amount:
    - Choice 1: **Apply extra to future obligations** (carry forward to next due periods).
    - Choice 2: **Overpay this specific invoice only** (extra goes to prepayment buffer or optional savings).
  - System records allocation strategy and impacts schedules accordingly.

#### 6.3 Reconciliation & Payment Status
- **Payment Tracking**:
  - External transaction IDs, provider reference, timestamps, status.
  - Map payments to invoices, goals, or generic wallet credits.
- **Reversals & Chargebacks**:
  - Ability to capture reversals from providers.
  - Adjust wallets and invoices accordingly with clear audit trail.

---

### 7. Loans Module

#### 7.1 Loan Products & Configuration
- **Per-Group Loan Settings**:
  - Interest rate(s) configured at group level (flat, reducing balance, or configurable model).
  - Max/min loan amounts (absolute or relative to savings).
  - Tenure options (e.g. 3, 6, 12 months).
  - Grace periods, penalty rules, collateral requirements.
- **Loan Types**:
  - **Secured Loans**: Backed by collateral (savings, guarantors, assets).
  - **Unsecured Loans**: Based on trust/credit limit.

#### 7.2 Loan Applications & Approval Workflow
- **Loan Application**:
  - Member specifies amount, tenure, purpose, and collateral (if any).
  - System checks:
    - Eligibility (membership status, savings history).
    - Group product rules (amount limits, frequency).
  - Application status: draft, submitted, under review, approved, rejected, disbursed, closed.
- **Multi-party Approvals**:
  - Configurable approval chains:
    - E.g. Loans Committee + Chairperson + Treasurer.
    - Threshold and quorum settings (e.g. at least 3 approvals, including at least 1 chairperson).
  - Approvers can comment or request additional info.

#### 7.3 Disbursement & Repayment
- **Disbursement**:
  - Disburse to member’s wallet.
  - Or log manual cash disbursement with references.
- **Repayment Schedules**:
  - Amortization schedule per loan:
    - Periodic principal + interest amount, due dates.
  - Integrate with invoices and payment module.
- **Repayment Sources**:
  - Direct repayment from wallet or external payment.
  - Allocation across principal, interest, penalties.

#### 7.4 Loan Position & Portfolio
- **Member View**:
  - Outstanding balance.
  - Next due date & amount.
  - Schedule and repayment history.
- **Group View**:
  - Total loan book.
  - NPL/overdue statistics.
  - Performance by product and member segment.

---

### 8. Events Module

#### 8.1 Event Management
- **Event Types**:
  - AGM (Annual General Meeting).
  - Leadership Meetings.
  - Committee Meetings.
  - Training / Onboarding sessions.
  - Custom event categories.
- **Event Details**:
  - Title, description.
  - Host group/organization.
  - Date, start/end times, timezone.
  - Location (physical address, virtual meeting link).
  - Capacity (optional).

#### 8.2 Attendees & Invitations
- **Attendee Selection**:
  - Invite:
    - All group members.
    - Specific roles (e.g. leadership, committee members).
    - Individual users.
  - Allow external guest emails (non-members) where needed.
- **RSVP & Attendance**:
  - RSVP status: invited, confirmed, declined, tentative.
  - Mark attendance on event date (e.g. via check-in).
  - Export attendance list.

#### 8.3 Event Notifications
- **Reminders**:
  - Pre-event reminders (e.g. 7 days, 1 day, 1 hour before).
  - On-date notifications (“Event starting now”).
  - Post-event follow-up (e.g. share minutes or decisions).

---

### 9. Reminders & Notifications

#### 9.1 Notification Types
- **Security & Account**:
  - New device or browser sign-in.
  - Password change success/failure.
  - Suspicious sign-in attempts (multiple failures).
  - Onboarding / welcome messages.
- **Payments & Obligations**:
  - Upcoming due payments (group or individual goals).
  - Overdue payments and penalty application.
  - Invoice creation, partial payment, and full payment confirmations.
  - Wallet top-ups, withdrawals, reversals.
- **Groups & Goals**:
  - New group or subgroup added.
  - Member added/removed from group.
  - New saving goal created or updated (group or personal).
  - Goal status changes (active → completed/paused/cancelled).
- **Loans**:
  - Loan application submitted (to applicant & approvers).
  - Loan approval/rejection.
  - Loan disbursement confirmation.
  - Loan schedule reminders and overdue notices.
- **Events**:
  - New event invitations.
  - Event reminders and updates.
  - Event cancellation or rescheduling.

#### 9.2 Delivery Channels
- **FCM App Notifications**:
  - Push notifications via Firebase Cloud Messaging for mobile/web apps.
- **Email**:
  - Transactional emails (receipts, confirmations).
  - Security alerts.
  - Event invitations and summaries.
- **SMS**:
  - Critical alerts (due/overdue payments, loan events).
  - OTPs and device sign-in notifications.

#### 9.3 Preferences & Routing
- **User Preferences**:
  - Per-notification-category opt-in/out.
  - Channel selection (app/email/SMS) per category.
- **Rate Limiting & Batching**:
  - Avoid spamming users with repeated reminders.
  - Daily digests where appropriate.

---

### 10. Finance & Accounting Module

#### 10.1 Invoicing & Billing
- **Invoice Generation**:
  - Automatic invoices from:
    - Savings obligations (group or personal goals).
    - Loan repayments.
    - Fees (membership fees, penalties, service charges).
  - Manual invoices for ad hoc charges.
- **Invoice Management**:
  - View, filter, and search invoices.
  - Edit/cancel invoices (with proper permissions).
  - Export invoices and statements.

#### 10.2 Payments & Integrated Tracking
- **Payment Integration**:
  - Connect to payment gateways for mobile money and card/bank payments.
  - Webhook endpoints for asynchronous updates.
- **Payment–Invoice Matching**:
  - Automatic matching by reference.
  - Manual matching tools for exceptions.

#### 10.3 Ledger & Accounting
- **Transaction Ledger**:
  - Double-entry or pseudo-ledger (configurable by implementation).
  - Each wallet operation recorded with:
    - Debit/credit, reference IDs, user/group, timestamps.
  - Support export for integration with external accounting systems (QuickBooks, etc.).
- **Disbursements & Withdrawals**:
  - Payout workflows (e.g. group distributing profits or dividends).
  - Approval flows for large disbursements.
  - Bank/mobile payout integration (optional).

#### 10.4 Portfolio & Reporting
- **Dashboards**:
  - Group and platform-level KPIs:
    - Total savings, total loans outstanding, delinquency rates, collected vs expected.
  - Goal completion rates and time-to-target metrics.
- **Reports**:
  - Member statements (savings, loans, payments).
  - Group statements (aggregated).
  - Aging reports for arrears.
  - Export in CSV/PDF formats.

---

### 11. Audit, Compliance & Logging

#### 11.1 Activity Logging
- **Audit Logs**:
  - Capture critical actions:
    - User logins, password changes.
    - Role assignments and leadership position changes.
    - Group creation/modification.
    - Goal creation/updates/completions.
    - Wallet transactions, invoice changes.
    - Loan applications, approvals, and disbursements.
  - Include: actor, timestamp, IP/device, before/after snapshots (where appropriate).

#### 11.2 Compliance Tools
- **KYC/AML Support (optional)**:
  - Capture ID data and documents.
  - Flag high-risk accounts/actions for manual review.
- **Export for Regulators**:
  - Generate reports required by regulators or auditors.

---

### 12. Administration & Configuration

#### 12.1 Platform Admin
- **Global Settings**:
  - Supported currencies.
  - Default notification settings.
  - Default roles and permission templates.
  - Payment provider configurations.
- **Tenant/Organization Management** (if multi-tenant):
  - Create and manage organizations.
  - Assign organization admins.

#### 12.2 Group-Level Configuration
- **Group Policies**:
  - Goal creation permissions.
  - Loan rules and approval chains.
  - Penalty and fee structures.
  - Membership rules (min/max members, membership fees).

---

### 13. Non-Functional Requirements (High-Level)

- **Security**:
  - Encrypted storage for sensitive data where possible.
  - HTTPS-only communication.
  - Role/permission checks at API and UI layers.
- **Scalability**:
  - Designed to handle many groups and members.
  - Asynchronous processing for notifications and payment webhooks.
- **Reliability**:
  - Idempotent payment processing to avoid duplicates.
  - Graceful handling of provider timeouts and retries.
- **Auditability**:
  - All financial-impacting actions are traceable.

---

*System Name: Save Mo Finance*  
*This document describes the target feature set for the Save Mo Finance platform and can be refined further as implementation details and constraints are finalized.*
