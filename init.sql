-- MySQL dump 10.13  Distrib 8.0.28, for Win64 (x86_64)
--
-- Host: localhost    Database: levels_living_db_new
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `assembly_queue`
--

DROP TABLE IF EXISTS `assembly_queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assembly_queue` (
  `queue_id` varchar(36) NOT NULL DEFAULT (uuid()),
  `order_id` varchar(36) NOT NULL,
  `item_id` varchar(36) NOT NULL,
  `priority` int DEFAULT '1',
  `assigned_to` varchar(36) DEFAULT NULL,
  `status` enum('pending','in_progress','completed','defective','on_hold') DEFAULT 'pending',
  `estimated_time` int DEFAULT NULL,
  `actual_time` int DEFAULT NULL,
  `started_at` timestamp NULL DEFAULT NULL,
  `completed_at` timestamp NULL DEFAULT NULL,
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`queue_id`),
  KEY `item_id` (`item_id`),
  KEY `assigned_to` (`assigned_to`),
  KEY `idx_assembly_queue_order` (`order_id`),
  KEY `idx_assembly_queue_status` (`status`),
  KEY `idx_assembly_queue_priority` (`priority`),
  CONSTRAINT `assembly_queue_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE,
  CONSTRAINT `assembly_queue_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `order_items` (`item_id`) ON DELETE CASCADE,
  CONSTRAINT `assembly_queue_ibfk_3` FOREIGN KEY (`assigned_to`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `communications`
--

DROP TABLE IF EXISTS `communications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `communications` (
  `communication_id` varchar(36) NOT NULL DEFAULT (uuid()),
  `order_id` varchar(36) DEFAULT NULL,
  `customer_id` varchar(36) DEFAULT NULL,
  `communication_type` enum('sms','email','push_notification','whatsapp','voice_call') NOT NULL,
  `message_type` enum('order_confirmation','delivery_scheduled','delivery_update','delivery_completed','adhoc_delivery_confirmation','delivery_failed','rescheduled','reminder','feedback_request','promotional') NOT NULL,
  `recipient_contact` varchar(50) NOT NULL,
  `recipient_name` varchar(100) DEFAULT NULL,
  `subject` text,
  `message_content` text NOT NULL,
  `scheduled_at` timestamp NULL DEFAULT NULL,
  `sent_at` timestamp NULL DEFAULT NULL,
  `delivered_at` timestamp NULL DEFAULT NULL,
  `read_at` timestamp NULL DEFAULT NULL,
  `status` enum('pending','scheduled','sent','delivered','read','failed','cancelled','bounced') DEFAULT 'pending',
  `failure_reason` text,
  `external_message_id` varchar(100) DEFAULT NULL,
  `external_status` varchar(50) DEFAULT NULL,
  `delivery_confirmation` json DEFAULT NULL,
  `priority` enum('low','normal','high','urgent') DEFAULT 'normal',
  `cost` decimal(6,4) DEFAULT NULL,
  `retry_count` int DEFAULT '0',
  `max_retries` int DEFAULT '3',
  `metadata` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`communication_id`),
  KEY `idx_communications_order` (`order_id`),
  KEY `idx_communications_customer` (`customer_id`),
  KEY `idx_communications_status` (`status`),
  KEY `idx_communications_type` (`communication_type`),
  KEY `idx_communications_sent` (`sent_at`),
  KEY `idx_communications_scheduled` (`scheduled_at`),
  CONSTRAINT `communications_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE,
  CONSTRAINT `communications_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `customer_id` varchar(36) NOT NULL DEFAULT (uuid()),
  `customer_name` varchar(100) NOT NULL,
  `customer_contact` varchar(20) DEFAULT NULL,
  `customer_street` varchar(200) DEFAULT NULL,
  `customer_unit` varchar(20) DEFAULT NULL,
  `customer_postal_code` varchar(6) NOT NULL,
  `housing_type` enum('HDB','Condo','Landed','Commercial') DEFAULT NULL,
  `communication_preferences` json DEFAULT (_utf8mb4'{"sms": true, "email": false}'),
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`customer_id`),
  UNIQUE KEY `customer_contact` (`customer_contact`),
  KEY `idx_customers_contact` (`customer_contact`),
  KEY `idx_customers_postal` (`customer_postal_code`),
  KEY `idx_customers_location` (`latitude`,`longitude`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `defects`
--

DROP TABLE IF EXISTS `defects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `defects` (
  `defect_id` varchar(36) NOT NULL DEFAULT (uuid()),
  `item_id` varchar(36) NOT NULL,
  `order_id` varchar(36) NOT NULL,
  `defect_type` varchar(50) NOT NULL,
  `description` text NOT NULL,
  `reported_by` varchar(36) DEFAULT NULL,
  `severity` enum('low','medium','high','critical') DEFAULT 'medium',
  `status` enum('reported','investigating','resolved','replaced') DEFAULT 'reported',
  `reported_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `resolved_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`defect_id`),
  KEY `reported_by` (`reported_by`),
  KEY `idx_defects_item` (`item_id`),
  KEY `idx_defects_order` (`order_id`),
  KEY `idx_defects_status` (`status`),
  CONSTRAINT `defects_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `order_items` (`item_id`) ON DELETE CASCADE,
  CONSTRAINT `defects_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE,
  CONSTRAINT `defects_ibfk_3` FOREIGN KEY (`reported_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `deliveries`
--

DROP TABLE IF EXISTS `deliveries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deliveries` (
  `delivery_id` varchar(36) NOT NULL DEFAULT (uuid()),
  `order_id` varchar(36) NOT NULL,
  `route_id` varchar(50) DEFAULT NULL,
  `delivery_date` date NOT NULL,
  `delivery_time_start` time DEFAULT NULL,
  `delivery_time_end` time DEFAULT NULL,
  `delivery_order` int DEFAULT NULL,
  `team` varchar(50) DEFAULT NULL,
  `driver_id` varchar(20) DEFAULT NULL,
  `customer_id` varchar(36) NOT NULL,
  `delivery_address` json NOT NULL,
  `delivered` tinyint(1) DEFAULT '0',
  `signature_data` text,
  `delivery_photos` json DEFAULT NULL,
  `delivery_notes` text,
  `customer_feedback` json DEFAULT NULL,
  `status` enum('scheduled','scheduled_adhoc','assigned','dispatched','in_transit','arrived','delivered','failed','rescheduled','returned','cancelled') DEFAULT 'scheduled',
  `failure_reason` text,
  `attempted_at` timestamp NULL DEFAULT NULL,
  `delivered_at` timestamp NULL DEFAULT NULL,
  `delivery_duration` int DEFAULT NULL,
  `special_instructions` text,
  `customer_availability_window` varchar(50) DEFAULT NULL,
  `requires_appointment` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`delivery_id`),
  KEY `route_id` (`route_id`),
  KEY `customer_id` (`customer_id`),
  KEY `idx_deliveries_order` (`order_id`),
  KEY `idx_deliveries_driver` (`driver_id`),
  KEY `idx_deliveries_date` (`delivery_date`),
  KEY `idx_deliveries_status` (`status`),
  CONSTRAINT `deliveries_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE,
  CONSTRAINT `deliveries_ibfk_2` FOREIGN KEY (`route_id`) REFERENCES `routes` (`route_id`) ON DELETE SET NULL,
  CONSTRAINT `deliveries_ibfk_3` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`driver_id`) ON DELETE SET NULL,
  CONSTRAINT `deliveries_ibfk_4` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `delivery_schedule`
--

DROP TABLE IF EXISTS `delivery_schedule`;
/*!50001 DROP VIEW IF EXISTS `delivery_schedule`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `delivery_schedule` AS SELECT 
 1 AS `delivery_id`,
 1 AS `delivery_date`,
 1 AS `delivery_time_start`,
 1 AS `delivery_time_end`,
 1 AS `delivery_order`,
 1 AS `status`,
 1 AS `order_no`,
 1 AS `customer_contact`,
 1 AS `customer_street`,
 1 AS `customer_postal_code`,
 1 AS `driver_name`,
 1 AS `team`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `delivery_schedules`
--

DROP TABLE IF EXISTS `delivery_schedules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_schedules` (
  `schedule_id` varchar(36) NOT NULL DEFAULT (uuid()),
  `schedule_date` date NOT NULL COMMENT 'Delivery date for this schedule',
  `driver_id` varchar(20) DEFAULT NULL COMMENT 'Assigned driver',
  `team` varchar(50) DEFAULT NULL COMMENT 'Delivery team name',
  `route_id` varchar(50) DEFAULT NULL COMMENT 'Link to routes table after route optimization',
  `total_locations` int DEFAULT '0' COMMENT 'Current number of delivery locations',
  `max_locations` int DEFAULT '18' COMMENT '3rd party delivery agreement: max 18 locations/day',
  `remaining_capacity` int GENERATED ALWAYS AS ((`max_locations` - `total_locations`)) STORED COMMENT 'Auto-calculated remaining slots',
  `is_full` tinyint(1) GENERATED ALWAYS AS ((`total_locations` >= `max_locations`)) STORED COMMENT 'Auto-calculated: is schedule full?',
  `status` enum('draft','confirmed','in_progress','completed','cancelled') DEFAULT 'draft',
  `start_time` time DEFAULT '09:00:00' COMMENT 'Delivery start time',
  `estimated_end_time` time DEFAULT NULL COMMENT 'Estimated completion time',
  `actual_end_time` time DEFAULT NULL COMMENT 'Actual completion time',
  `route_polyline` longtext COMMENT 'Google Maps polyline for route visualization',
  `total_distance_meters` int DEFAULT NULL COMMENT 'Total route distance',
  `total_duration_seconds` int DEFAULT NULL COMMENT 'Total route duration',
  `notes` text,
  `created_by` varchar(36) DEFAULT NULL COMMENT 'User who created this schedule',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`schedule_id`),
  KEY `route_id` (`route_id`),
  KEY `created_by` (`created_by`),
  KEY `idx_schedule_date` (`schedule_date`),
  KEY `idx_schedule_status` (`status`),
  KEY `idx_schedule_driver` (`driver_id`),
  KEY `idx_schedule_capacity` (`schedule_date`,`is_full`),
  CONSTRAINT `delivery_schedules_ibfk_1` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`driver_id`) ON DELETE SET NULL,
  CONSTRAINT `delivery_schedules_ibfk_2` FOREIGN KEY (`route_id`) REFERENCES `routes` (`route_id`) ON DELETE SET NULL,
  CONSTRAINT `delivery_schedules_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Daily delivery schedules with 18 location capacity limit';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `drivers`
--

DROP TABLE IF EXISTS `drivers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drivers` (
  `driver_id` varchar(20) NOT NULL,
  `driver_name` varchar(100) NOT NULL,
  `driver_contact` varchar(20) NOT NULL,
  `email` varchar(200) DEFAULT NULL,
  `team` varchar(50) DEFAULT NULL,
  `license_number` varchar(20) DEFAULT NULL,
  `license_expiry` date DEFAULT NULL,
  `vehicle_type` enum('van','truck','motorcycle','car') DEFAULT NULL,
  `vehicle_plate` varchar(20) DEFAULT NULL,
  `vehicle_capacity_kg` decimal(8,2) DEFAULT NULL,
  `vehicle_capacity_cbm` decimal(8,2) DEFAULT NULL,
  `max_delivery_items` int DEFAULT NULL,
  `status` enum('available','on_delivery','off_duty','maintenance','on_leave') DEFAULT 'available',
  `base_hourly_rate` decimal(8,2) DEFAULT NULL,
  `overtime_rate` decimal(4,2) DEFAULT '1.50',
  `weekend_rate` decimal(4,2) DEFAULT '2.00',
  `performance_rating` decimal(3,2) DEFAULT '5.00',
  `hire_date` date DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`driver_id`),
  UNIQUE KEY `driver_contact` (`driver_contact`),
  UNIQUE KEY `license_number` (`license_number`),
  UNIQUE KEY `vehicle_plate` (`vehicle_plate`),
  KEY `idx_drivers_status` (`status`),
  KEY `idx_drivers_team` (`team`),
  CONSTRAINT `chk_driver_contact` CHECK (regexp_like(`driver_contact`,_utf8mb4'^(\\+65)?[689][0-9]{7}$'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventory`
--

DROP TABLE IF EXISTS `inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory` (
  `sku` varchar(100) NOT NULL,
  `item_name` varchar(200) NOT NULL,
  `variant` varchar(100) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `subcategory` varchar(100) DEFAULT NULL,
  `description` text,
  `unit_price` decimal(10,2) DEFAULT NULL,
  `weight_per_unit` decimal(8,2) DEFAULT NULL,
  `volume_per_unit` decimal(8,2) DEFAULT NULL,
  `dimensions` json DEFAULT NULL,
  `delivery_type` enum('standard','express','heavy_item','large_item','fragile','special_handling','white_glove','assembly_required','showroom_pickup') DEFAULT 'standard',
  `special_handling_required` tinyint(1) DEFAULT '0',
  `assembly_required` tinyint(1) DEFAULT '0',
  `showroom_item` tinyint(1) DEFAULT '0',
  `handling_instructions` text,
  `storage_location` varchar(50) DEFAULT NULL,
  `supplier` varchar(200) DEFAULT NULL,
  `supplier_sku` varchar(100) DEFAULT NULL,
  `image_urls` json DEFAULT NULL,
  `product_tags` json DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`sku`),
  KEY `idx_inventory_category` (`category`),
  KEY `idx_inventory_delivery_type` (`delivery_type`),
  KEY `idx_inventory_name` (`item_name`),
  KEY `idx_inventory_variant` (`variant`),
  KEY `idx_inventory_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `inventory_delivery_requirements`
--

DROP TABLE IF EXISTS `inventory_delivery_requirements`;
/*!50001 DROP VIEW IF EXISTS `inventory_delivery_requirements`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `inventory_delivery_requirements` AS SELECT 
 1 AS `sku`,
 1 AS `item_name`,
 1 AS `variant`,
 1 AS `category`,
 1 AS `delivery_type`,
 1 AS `weight_per_unit`,
 1 AS `volume_per_unit`,
 1 AS `special_handling_required`,
 1 AS `assembly_required`,
 1 AS `showroom_item`,
 1 AS `delivery_notes`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `item_id` varchar(36) NOT NULL DEFAULT (uuid()),
  `order_id` varchar(36) NOT NULL,
  `sku` varchar(100) NOT NULL,
  `item_name` varchar(200) NOT NULL,
  `variant` varchar(100) DEFAULT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  `unit_price` decimal(10,2) DEFAULT NULL,
  `total_price` decimal(12,2) DEFAULT NULL,
  `assembled` tinyint(1) DEFAULT '0',
  `assembly_notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`item_id`),
  KEY `idx_order_items_order` (`order_id`),
  KEY `idx_order_items_sku` (`sku`),
  KEY `idx_order_items_assembled` (`assembled`),
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE,
  CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`sku`) REFERENCES `inventory` (`sku`) ON DELETE RESTRICT,
  CONSTRAINT `chk_quantity` CHECK ((`quantity` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `order_summary`
--

DROP TABLE IF EXISTS `order_summary`;
/*!50001 DROP VIEW IF EXISTS `order_summary`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `order_summary` AS SELECT 
 1 AS `order_id`,
 1 AS `order_no`,
 1 AS `status`,
 1 AS `order_date`,
 1 AS `order_value`,
 1 AS `customer_contact`,
 1 AS `customer_postal_code`,
 1 AS `housing_type`,
 1 AS `total_items`,
 1 AS `assembled_items`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `order_id` varchar(36) NOT NULL DEFAULT (uuid()),
  `order_no` varchar(50) NOT NULL,
  `shopify_order_id` varchar(50) DEFAULT NULL,
  `platform_order_id` varchar(50) DEFAULT NULL,
  `customer_id` varchar(36) NOT NULL,
  `status` enum('received','validated','processing','in_assembly','ready_for_delivery','out_for_delivery','delivered','failed','cancelled','returned') DEFAULT 'received',
  `order_type` enum('pre_order','asap','adhoc','custom') DEFAULT 'pre_order',
  `preferred_delivery_date` date DEFAULT NULL COMMENT 'Customer preferred delivery date (for custom_date type)',
  `preferred_delivery_time` varchar(50) DEFAULT NULL COMMENT 'Customer preferred delivery time slot from remarks',
  `is_scheduled` tinyint(1) DEFAULT '0' COMMENT 'Whether order has been scheduled by HQ (0=No, 1=Yes)',
  `scheduled_delivery_date` date DEFAULT NULL COMMENT 'Actual date scheduled by system',
  `scheduled_by` varchar(36) DEFAULT NULL COMMENT 'User ID who scheduled this order',
  `scheduled_at` timestamp NULL DEFAULT NULL COMMENT 'When order was scheduled',
  `delivery_completed` tinyint(1) DEFAULT '0' COMMENT 'Whether delivery is completed (0=No, 1=Yes)',
  `order_date` date NOT NULL,
  `order_value` decimal(12,2) NOT NULL DEFAULT '0.00',
  `currency` varchar(3) DEFAULT 'SGD',
  `tag` varchar(100) DEFAULT NULL,
  `note` text,
  `remarks` text COMMENT 'Internal remarks/notes added by HQ for scheduling purposes',
  `custom_fields` json DEFAULT NULL,
  `special_delivery` tinyint(1) DEFAULT '0',
  `priority` int DEFAULT '1',
  `source_system` varchar(50) DEFAULT 'shopify',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`order_id`),
  UNIQUE KEY `order_no` (`order_no`),
  KEY `idx_orders_customer` (`customer_id`),
  KEY `idx_orders_status` (`status`),
  KEY `idx_orders_date` (`order_date`),
  KEY `idx_orders_no` (`order_no`),
  KEY `idx_orders_type` (`order_type`),
  KEY `idx_orders_scheduled` (`is_scheduled`,`scheduled_delivery_date`),
  KEY `idx_orders_completed` (`delivery_completed`),
  KEY `fk_orders_scheduled_by` (`scheduled_by`),
  CONSTRAINT `fk_orders_scheduled_by` FOREIGN KEY (`scheduled_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`) ON DELETE CASCADE,
  CONSTRAINT `chk_order_value` CHECK ((`order_value` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `routes`
--

DROP TABLE IF EXISTS `routes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `routes` (
  `route_id` varchar(50) NOT NULL,
  `driver_id` varchar(20) DEFAULT NULL,
  `team` varchar(50) DEFAULT NULL,
  `route_date` date NOT NULL,
  `route_type` enum('regular','adhoc_single_delivery','split_load','return_trip') DEFAULT 'regular',
  `start_location` json NOT NULL,
  `end_location` json DEFAULT NULL,
  `waypoints` json DEFAULT NULL,
  `route_data` json DEFAULT NULL,
  `total_distance` decimal(8,2) DEFAULT NULL,
  `estimated_time` int DEFAULT NULL,
  `actual_time` int DEFAULT NULL,
  `fuel_cost` decimal(8,2) DEFAULT NULL,
  `toll_cost` decimal(8,2) DEFAULT NULL,
  `additional_cost` decimal(10,2) DEFAULT '0.00',
  `overtime_hours` decimal(4,2) DEFAULT '0.00',
  `overtime_applicable` tinyint(1) DEFAULT '0',
  `weekend_surcharge` tinyint(1) DEFAULT '0',
  `status` enum('planned','assigned','in_progress','completed','cancelled') DEFAULT 'planned',
  `optimization_score` decimal(5,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`route_id`),
  KEY `idx_routes_driver` (`driver_id`),
  KEY `idx_routes_date` (`route_date`),
  KEY `idx_routes_status` (`status`),
  CONSTRAINT `routes_ibfk_1` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`driver_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `schedule_orders`
--

DROP TABLE IF EXISTS `schedule_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schedule_orders` (
  `schedule_order_id` varchar(36) NOT NULL DEFAULT (uuid()),
  `schedule_id` varchar(36) NOT NULL COMMENT 'Link to delivery_schedules',
  `order_id` varchar(36) NOT NULL COMMENT 'Link to orders',
  `delivery_id` varchar(36) DEFAULT NULL COMMENT 'Link to deliveries table when delivery is created',
  `sequence_number` int NOT NULL COMMENT 'Delivery sequence (1-18, sorted by postal code)',
  `postal_code` varchar(6) NOT NULL COMMENT 'Customer postal code (cached for sorting)',
  `latitude` decimal(10,8) DEFAULT NULL COMMENT 'Customer latitude (cached)',
  `longitude` decimal(11,8) DEFAULT NULL COMMENT 'Customer longitude (cached)',
  `estimated_arrival_time` time DEFAULT NULL COMMENT 'Estimated arrival time at this location',
  `actual_arrival_time` time DEFAULT NULL COMMENT 'Actual arrival time',
  `estimated_duration_minutes` int DEFAULT '30' COMMENT 'Estimated time at this location',
  `actual_duration_minutes` int DEFAULT NULL COMMENT 'Actual time spent',
  `status` enum('scheduled','in_transit','arrived','delivered','failed','skipped') DEFAULT 'scheduled',
  `requires_warehouse_return` tinyint(1) DEFAULT '0' COMMENT 'If customer has multiple items, driver returns to warehouse',
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`schedule_order_id`),
  UNIQUE KEY `unique_schedule_order` (`schedule_id`,`order_id`),
  KEY `order_id` (`order_id`),
  KEY `delivery_id` (`delivery_id`),
  KEY `idx_schedule_orders_sequence` (`schedule_id`,`sequence_number`),
  KEY `idx_schedule_orders_status` (`status`),
  CONSTRAINT `schedule_orders_ibfk_1` FOREIGN KEY (`schedule_id`) REFERENCES `delivery_schedules` (`schedule_id`) ON DELETE CASCADE,
  CONSTRAINT `schedule_orders_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE,
  CONSTRAINT `schedule_orders_ibfk_3` FOREIGN KEY (`delivery_id`) REFERENCES `deliveries` (`delivery_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Junction table linking orders to daily schedules with sequence';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_events`
--

DROP TABLE IF EXISTS `system_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_events` (
  `event_id` varchar(36) NOT NULL DEFAULT (uuid()),
  `event_type` varchar(50) NOT NULL,
  `service_name` varchar(50) NOT NULL,
  `entity_type` varchar(30) NOT NULL,
  `entity_id` varchar(36) NOT NULL,
  `event_data` json DEFAULT NULL,
  `user_id` varchar(36) DEFAULT NULL,
  `session_id` varchar(36) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text,
  `correlation_id` varchar(36) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`event_id`),
  KEY `idx_system_events_service` (`service_name`),
  KEY `idx_system_events_type` (`event_type`),
  KEY `idx_system_events_entity` (`entity_type`,`entity_id`),
  KEY `idx_system_events_user` (`user_id`),
  KEY `idx_system_events_created` (`created_at`),
  CONSTRAINT `system_events_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_sessions`
--

DROP TABLE IF EXISTS `user_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_sessions` (
  `session_id` varchar(36) NOT NULL DEFAULT (uuid()),
  `user_id` varchar(36) NOT NULL,
  `refresh_token_hash` varchar(200) NOT NULL,
  `expires_at` timestamp NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_used` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user_agent` text,
  `ip_address` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`session_id`),
  KEY `idx_sessions_user_id` (`user_id`),
  KEY `idx_sessions_expires` (`expires_at`),
  CONSTRAINT `user_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` varchar(36) NOT NULL DEFAULT (uuid()),
  `email` varchar(200) NOT NULL,
  `password_hash` varchar(200) NOT NULL,
  `role` enum('admin','warehouse','driver','hq','customer_service') NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `last_login` timestamp NULL DEFAULT NULL,
  `login_attempts` int DEFAULT '0',
  `locked_until` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_users_email` (`email`),
  KEY `idx_users_role` (`role`),
  KEY `idx_users_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `v_scheduled_deliveries`
--

DROP TABLE IF EXISTS `v_scheduled_deliveries`;
/*!50001 DROP VIEW IF EXISTS `v_scheduled_deliveries`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_scheduled_deliveries` AS SELECT 
 1 AS `schedule_id`,
 1 AS `schedule_date`,
 1 AS `driver_id`,
 1 AS `driver_name`,
 1 AS `driver_contact`,
 1 AS `team`,
 1 AS `total_locations`,
 1 AS `max_locations`,
 1 AS `remaining_capacity`,
 1 AS `schedule_status`,
 1 AS `start_time`,
 1 AS `estimated_end_time`,
 1 AS `schedule_order_id`,
 1 AS `sequence_number`,
 1 AS `estimated_arrival_time`,
 1 AS `actual_arrival_time`,
 1 AS `delivery_status`,
 1 AS `order_id`,
 1 AS `order_no`,
 1 AS `shopify_order_id`,
 1 AS `order_type`,
 1 AS `order_value`,
 1 AS `customer_name`,
 1 AS `customer_contact`,
 1 AS `customer_postal_code`,
 1 AS `customer_street`,
 1 AS `customer_unit`,
 1 AS `housing_type`,
 1 AS `total_items`,
 1 AS `requires_warehouse_return`,
 1 AS `latitude`,
 1 AS `longitude`,
 1 AS `route_polyline`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_todays_deliveries`
--

DROP TABLE IF EXISTS `v_todays_deliveries`;
/*!50001 DROP VIEW IF EXISTS `v_todays_deliveries`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_todays_deliveries` AS SELECT 
 1 AS `schedule_order_id`,
 1 AS `sequence_number`,
 1 AS `schedule_date`,
 1 AS `driver_id`,
 1 AS `driver_name`,
 1 AS `driver_contact`,
 1 AS `order_no`,
 1 AS `order_type`,
 1 AS `customer_name`,
 1 AS `customer_contact`,
 1 AS `customer_postal_code`,
 1 AS `customer_street`,
 1 AS `customer_unit`,
 1 AS `housing_type`,
 1 AS `estimated_arrival_time`,
 1 AS `actual_arrival_time`,
 1 AS `delivery_status`,
 1 AS `total_items`,
 1 AS `requires_warehouse_return`,
 1 AS `latitude`,
 1 AS `longitude`,
 1 AS `route_polyline`,
 1 AS `notes`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_unscheduled_orders`
--

DROP TABLE IF EXISTS `v_unscheduled_orders`;
/*!50001 DROP VIEW IF EXISTS `v_unscheduled_orders`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_unscheduled_orders` AS SELECT 
 1 AS `order_id`,
 1 AS `order_no`,
 1 AS `shopify_order_id`,
 1 AS `order_type`,
 1 AS `preferred_delivery_date`,
 1 AS `preferred_delivery_time`,
 1 AS `order_status`,
 1 AS `order_date`,
 1 AS `order_value`,
 1 AS `order_remarks`,
 1 AS `remarks`,
 1 AS `customer_id`,
 1 AS `customer_name`,
 1 AS `customer_contact`,
 1 AS `customer_postal_code`,
 1 AS `customer_street`,
 1 AS `customer_unit`,
 1 AS `housing_type`,
 1 AS `latitude`,
 1 AS `longitude`,
 1 AS `total_items`,
 1 AS `items_requiring_assembly`,
 1 AS `created_at`,
 1 AS `updated_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `delivery_schedule`
--

/*!50001 DROP VIEW IF EXISTS `delivery_schedule`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `delivery_schedule` AS select `d`.`delivery_id` AS `delivery_id`,`d`.`delivery_date` AS `delivery_date`,`d`.`delivery_time_start` AS `delivery_time_start`,`d`.`delivery_time_end` AS `delivery_time_end`,`d`.`delivery_order` AS `delivery_order`,`d`.`status` AS `status`,`o`.`order_no` AS `order_no`,`c`.`customer_contact` AS `customer_contact`,`c`.`customer_street` AS `customer_street`,`c`.`customer_postal_code` AS `customer_postal_code`,`dr`.`driver_name` AS `driver_name`,`d`.`team` AS `team` from (((`deliveries` `d` join `orders` `o` on((`d`.`order_id` = `o`.`order_id`))) join `customers` `c` on((`o`.`customer_id` = `c`.`customer_id`))) left join `drivers` `dr` on((`d`.`driver_id` = `dr`.`driver_id`))) order by `d`.`delivery_date`,`d`.`delivery_order` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `inventory_delivery_requirements`
--

/*!50001 DROP VIEW IF EXISTS `inventory_delivery_requirements`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `inventory_delivery_requirements` AS select `inventory`.`sku` AS `sku`,`inventory`.`item_name` AS `item_name`,`inventory`.`variant` AS `variant`,`inventory`.`category` AS `category`,`inventory`.`delivery_type` AS `delivery_type`,`inventory`.`weight_per_unit` AS `weight_per_unit`,`inventory`.`volume_per_unit` AS `volume_per_unit`,`inventory`.`special_handling_required` AS `special_handling_required`,`inventory`.`assembly_required` AS `assembly_required`,`inventory`.`showroom_item` AS `showroom_item`,(case when (`inventory`.`delivery_type` = 'heavy_item') then 'Requires heavy lifting equipment' when (`inventory`.`delivery_type` = 'fragile') then 'Handle with extra care' when (`inventory`.`delivery_type` = 'white_glove') then 'Full service delivery and setup' when (`inventory`.`assembly_required` = true) then 'Assembly required' when (`inventory`.`showroom_item` = true) then 'Pickup from showroom required' else 'Standard delivery' end) AS `delivery_notes` from `inventory` where (`inventory`.`is_active` = true) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `order_summary`
--

/*!50001 DROP VIEW IF EXISTS `order_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `order_summary` AS select `o`.`order_id` AS `order_id`,`o`.`order_no` AS `order_no`,`o`.`status` AS `status`,`o`.`order_date` AS `order_date`,`o`.`order_value` AS `order_value`,`c`.`customer_contact` AS `customer_contact`,`c`.`customer_postal_code` AS `customer_postal_code`,`c`.`housing_type` AS `housing_type`,count(`oi`.`item_id`) AS `total_items`,count((case when (`oi`.`assembled` = true) then 1 end)) AS `assembled_items` from ((`orders` `o` join `customers` `c` on((`o`.`customer_id` = `c`.`customer_id`))) left join `order_items` `oi` on((`o`.`order_id` = `oi`.`order_id`))) group by `o`.`order_id`,`c`.`customer_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_scheduled_deliveries`
--

/*!50001 DROP VIEW IF EXISTS `v_scheduled_deliveries`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = latin1 */;
/*!50001 SET character_set_results     = latin1 */;
/*!50001 SET collation_connection      = latin1_swedish_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_scheduled_deliveries` AS select `ds`.`schedule_id` AS `schedule_id`,`ds`.`schedule_date` AS `schedule_date`,`ds`.`driver_id` AS `driver_id`,`d`.`driver_name` AS `driver_name`,`d`.`driver_contact` AS `driver_contact`,`ds`.`team` AS `team`,`ds`.`total_locations` AS `total_locations`,`ds`.`max_locations` AS `max_locations`,`ds`.`remaining_capacity` AS `remaining_capacity`,`ds`.`status` AS `schedule_status`,`ds`.`start_time` AS `start_time`,`ds`.`estimated_end_time` AS `estimated_end_time`,`so`.`schedule_order_id` AS `schedule_order_id`,`so`.`sequence_number` AS `sequence_number`,`so`.`estimated_arrival_time` AS `estimated_arrival_time`,`so`.`actual_arrival_time` AS `actual_arrival_time`,`so`.`status` AS `delivery_status`,`o`.`order_id` AS `order_id`,`o`.`order_no` AS `order_no`,`o`.`shopify_order_id` AS `shopify_order_id`,`o`.`order_type` AS `order_type`,`o`.`order_value` AS `order_value`,`c`.`customer_name` AS `customer_name`,`c`.`customer_contact` AS `customer_contact`,`c`.`customer_postal_code` AS `customer_postal_code`,`c`.`customer_street` AS `customer_street`,`c`.`customer_unit` AS `customer_unit`,`c`.`housing_type` AS `housing_type`,count(`oi`.`item_id`) AS `total_items`,`so`.`requires_warehouse_return` AS `requires_warehouse_return`,`so`.`latitude` AS `latitude`,`so`.`longitude` AS `longitude`,`ds`.`route_polyline` AS `route_polyline` from (((((`delivery_schedules` `ds` join `schedule_orders` `so` on((`ds`.`schedule_id` = `so`.`schedule_id`))) join `orders` `o` on((`so`.`order_id` = `o`.`order_id`))) join `customers` `c` on((`o`.`customer_id` = `c`.`customer_id`))) left join `drivers` `d` on((`ds`.`driver_id` = `d`.`driver_id`))) left join `order_items` `oi` on((`o`.`order_id` = `oi`.`order_id`))) group by `ds`.`schedule_id`,`ds`.`schedule_date`,`ds`.`driver_id`,`d`.`driver_name`,`d`.`driver_contact`,`ds`.`team`,`ds`.`total_locations`,`ds`.`max_locations`,`ds`.`remaining_capacity`,`ds`.`status`,`ds`.`start_time`,`ds`.`estimated_end_time`,`so`.`schedule_order_id`,`so`.`sequence_number`,`so`.`estimated_arrival_time`,`so`.`actual_arrival_time`,`so`.`status`,`o`.`order_id`,`o`.`order_no`,`o`.`shopify_order_id`,`o`.`order_type`,`o`.`order_value`,`c`.`customer_name`,`c`.`customer_contact`,`c`.`customer_postal_code`,`c`.`customer_street`,`c`.`customer_unit`,`c`.`housing_type`,`so`.`requires_warehouse_return`,`so`.`latitude`,`so`.`longitude`,`ds`.`route_polyline` order by `ds`.`schedule_date` desc,`so`.`sequence_number` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_todays_deliveries`
--

/*!50001 DROP VIEW IF EXISTS `v_todays_deliveries`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = latin1 */;
/*!50001 SET character_set_results     = latin1 */;
/*!50001 SET collation_connection      = latin1_swedish_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_todays_deliveries` AS select `so`.`schedule_order_id` AS `schedule_order_id`,`so`.`sequence_number` AS `sequence_number`,`ds`.`schedule_date` AS `schedule_date`,`ds`.`driver_id` AS `driver_id`,`d`.`driver_name` AS `driver_name`,`d`.`driver_contact` AS `driver_contact`,`o`.`order_no` AS `order_no`,`o`.`order_type` AS `order_type`,`c`.`customer_name` AS `customer_name`,`c`.`customer_contact` AS `customer_contact`,`c`.`customer_postal_code` AS `customer_postal_code`,`c`.`customer_street` AS `customer_street`,`c`.`customer_unit` AS `customer_unit`,`c`.`housing_type` AS `housing_type`,`so`.`estimated_arrival_time` AS `estimated_arrival_time`,`so`.`actual_arrival_time` AS `actual_arrival_time`,`so`.`status` AS `delivery_status`,count(`oi`.`item_id`) AS `total_items`,`so`.`requires_warehouse_return` AS `requires_warehouse_return`,`so`.`latitude` AS `latitude`,`so`.`longitude` AS `longitude`,`ds`.`route_polyline` AS `route_polyline`,`so`.`notes` AS `notes` from (((((`schedule_orders` `so` join `delivery_schedules` `ds` on((`so`.`schedule_id` = `ds`.`schedule_id`))) join `orders` `o` on((`so`.`order_id` = `o`.`order_id`))) join `customers` `c` on((`o`.`customer_id` = `c`.`customer_id`))) left join `drivers` `d` on((`ds`.`driver_id` = `d`.`driver_id`))) left join `order_items` `oi` on((`o`.`order_id` = `oi`.`order_id`))) where ((`ds`.`schedule_date` = curdate()) and (`ds`.`status` in ('confirmed','in_progress'))) group by `so`.`schedule_order_id`,`so`.`sequence_number`,`ds`.`schedule_date`,`ds`.`driver_id`,`d`.`driver_name`,`d`.`driver_contact`,`o`.`order_no`,`o`.`order_type`,`c`.`customer_name`,`c`.`customer_contact`,`c`.`customer_postal_code`,`c`.`customer_street`,`c`.`customer_unit`,`c`.`housing_type`,`so`.`estimated_arrival_time`,`so`.`actual_arrival_time`,`so`.`status`,`so`.`requires_warehouse_return`,`so`.`latitude`,`so`.`longitude`,`ds`.`route_polyline`,`so`.`notes` order by `so`.`sequence_number` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_unscheduled_orders`
--

/*!50001 DROP VIEW IF EXISTS `v_unscheduled_orders`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = latin1 */;
/*!50001 SET character_set_results     = latin1 */;
/*!50001 SET collation_connection      = latin1_swedish_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_unscheduled_orders` AS select `o`.`order_id` AS `order_id`,`o`.`order_no` AS `order_no`,`o`.`shopify_order_id` AS `shopify_order_id`,`o`.`order_type` AS `order_type`,`o`.`preferred_delivery_date` AS `preferred_delivery_date`,`o`.`preferred_delivery_time` AS `preferred_delivery_time`,`o`.`status` AS `order_status`,`o`.`order_date` AS `order_date`,`o`.`order_value` AS `order_value`,`o`.`note` AS `order_remarks`,`o`.`remarks` AS `remarks`,`c`.`customer_id` AS `customer_id`,`c`.`customer_name` AS `customer_name`,`c`.`customer_contact` AS `customer_contact`,`c`.`customer_postal_code` AS `customer_postal_code`,`c`.`customer_street` AS `customer_street`,`c`.`customer_unit` AS `customer_unit`,`c`.`housing_type` AS `housing_type`,`c`.`latitude` AS `latitude`,`c`.`longitude` AS `longitude`,count(`oi`.`item_id`) AS `total_items`,sum((case when (`i`.`assembly_required` = 1) then 1 else 0 end)) AS `items_requiring_assembly`,`o`.`created_at` AS `created_at`,`o`.`updated_at` AS `updated_at` from (((`orders` `o` join `customers` `c` on((`o`.`customer_id` = `c`.`customer_id`))) left join `order_items` `oi` on((`o`.`order_id` = `oi`.`order_id`))) left join `inventory` `i` on((`oi`.`sku` = `i`.`sku`))) where ((`o`.`is_scheduled` = 0) and (`o`.`delivery_completed` = 0) and (`o`.`status` in ('validated','processing','ready_for_delivery'))) group by `o`.`order_id`,`o`.`order_no`,`o`.`shopify_order_id`,`o`.`order_type`,`o`.`preferred_delivery_date`,`o`.`preferred_delivery_time`,`o`.`status`,`o`.`order_date`,`o`.`order_value`,`o`.`note`,`o`.`remarks`,`c`.`customer_id`,`c`.`customer_name`,`c`.`customer_contact`,`c`.`customer_postal_code`,`c`.`customer_street`,`c`.`customer_unit`,`c`.`housing_type`,`c`.`latitude`,`c`.`longitude`,`o`.`created_at`,`o`.`updated_at` order by (case `o`.`order_type` when 'asap' then 1 when 'adhoc' then 2 when 'pre_order' then 3 when 'custom' then 4 else 5 end),`o`.`order_date` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `notification_id` varchar(36) NOT NULL,
  `recipient` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `channel` enum('sms','whatsapp','email') NOT NULL,
  `notification_type` varchar(50) NOT NULL,
  `external_id` varchar(255) DEFAULT NULL COMMENT 'Twilio message SID or external provider ID',
  `status` enum('pending','sent','delivered','failed','queued') DEFAULT 'pending',
  `error_message` text,
  `order_id` varchar(36) DEFAULT NULL,
  `customer_id` varchar(36) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`notification_id`),
  KEY `idx_notifications_order` (`order_id`),
  KEY `idx_notifications_customer` (`customer_id`),
  KEY `idx_notifications_status` (`status`),
  KEY `idx_notifications_channel` (`channel`),
  KEY `idx_notifications_created` (`created_at`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE SET NULL,
  CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Dump completed on 2025-10-08 13:44:39
