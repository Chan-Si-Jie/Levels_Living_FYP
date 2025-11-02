-- Create notifications table for NotificationMS
-- Execute this in MySQL Workbench or your preferred MySQL client

USE levels_living_db_new;

CREATE TABLE IF NOT EXISTS `notifications` (
  `notification_id` VARCHAR(36) NOT NULL PRIMARY KEY COMMENT 'UUID for the notification',
  `recipient` VARCHAR(255) NOT NULL COMMENT 'Phone number or email address',
  `message` TEXT NOT NULL COMMENT 'Notification message content',
  `channel` ENUM('sms','whatsapp','email') NOT NULL COMMENT 'Delivery channel',
  `notification_type` VARCHAR(50) NOT NULL COMMENT 'Type of notification (e.g., order_delivered, out_for_delivery)',
  `external_id` VARCHAR(255) DEFAULT NULL COMMENT 'Twilio message SID or external provider ID',
  `status` ENUM('pending','sent','delivered','failed','queued') DEFAULT 'pending' COMMENT 'Current status of the notification',
  `error_message` TEXT COMMENT 'Error details if notification failed',
  `order_id` VARCHAR(36) DEFAULT NULL COMMENT 'Related order ID',
  `customer_id` VARCHAR(36) DEFAULT NULL COMMENT 'Related customer ID',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When notification was created',
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update time',
  KEY `idx_notifications_order` (`order_id`),
  KEY `idx_notifications_customer` (`customer_id`),
  KEY `idx_notifications_status` (`status`),
  KEY `idx_notifications_channel` (`channel`),
  KEY `idx_notifications_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='Stores all notification records sent via SMS, WhatsApp, or Email';

-- Verify the table was created
SELECT 'Table created successfully!' AS status;
SHOW CREATE TABLE notifications;
