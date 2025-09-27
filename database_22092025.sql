CREATE DATABASE  IF NOT EXISTS `levels_living_db_new` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `levels_living_db_new`;
-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: levels_living_db_new
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+08:00' */;
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
-- Dumping data for table `assembly_queue`
--

LOCK TABLES `assembly_queue` WRITE;
/*!40000 ALTER TABLE `assembly_queue` DISABLE KEYS */;
/*!40000 ALTER TABLE `assembly_queue` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `communications`
--

LOCK TABLES `communications` WRITE;
/*!40000 ALTER TABLE `communications` DISABLE KEYS */;
/*!40000 ALTER TABLE `communications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `customer_id` varchar(36) NOT NULL DEFAULT (uuid()),
  `customer_contact` varchar(20) NOT NULL,
  `customer_street` varchar(200) DEFAULT NULL,
  `customer_unit` varchar(20) DEFAULT NULL,
  `customer_postal_code` varchar(6) NOT NULL,
  `housing_type` enum('HDB','Condo','Landed','Commercial') DEFAULT NULL,
  `delivery_preferences` json DEFAULT NULL,
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
  KEY `idx_customers_location` (`latitude`,`longitude`),
  CONSTRAINT `chk_contact` CHECK (regexp_like(`customer_contact`,_utf8mb4'^(\\+65)?[689][0-9]{7}$')),
  CONSTRAINT `chk_postal_code` CHECK (regexp_like(`customer_postal_code`,_utf8mb4'^[0-9]{6}$'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES ('4b6634dc-96c9-11f0-86bc-d2f552c411bd','+6598765432','456 Orchard Road','#05-67','238123','Condo',NULL,'{\"sms\": true, \"email\": false}',1.30480000,103.81980000,1,'2025-09-21 08:59:34','2025-09-21 08:59:34'),('4b6635fe-96c9-11f0-86bc-d2f552c411bd','+6587654321','789 Bukit Timah Road','House 1','259012','Landed',NULL,'{\"sms\": true, \"email\": false}',1.33870000,103.78900000,1,'2025-09-21 08:59:34','2025-09-21 08:59:34'),('59d67a1d-3d3d-482d-a532-94b0db80d54f','+6591234567','123 Ang Mo Kio Avenue 1','05-365','123456','HDB','{\"delivery_time\": \"business_hours\", \"contact_method\": \"phone\", \"delivery_window\": \"standard\", \"requires_appointment\": true, \"special_instructions\": null}','{\"sms\": false, \"email\": false, \"phone\": true, \"language\": \"en\", \"preferred_time\": \"business_hours\"}',1.30480000,103.83180000,0,'2025-09-22 22:23:48','2025-09-22 22:23:48');
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `defects`
--

LOCK TABLES `defects` WRITE;
/*!40000 ALTER TABLE `defects` DISABLE KEYS */;
/*!40000 ALTER TABLE `defects` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `deliveries`
--

LOCK TABLES `deliveries` WRITE;
/*!40000 ALTER TABLE `deliveries` DISABLE KEYS */;
/*!40000 ALTER TABLE `deliveries` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `drivers`
--

LOCK TABLES `drivers` WRITE;
/*!40000 ALTER TABLE `drivers` DISABLE KEYS */;
INSERT INTO `drivers` VALUES ('DRV001','John Tan','+6591111111',NULL,'Team A','DL123456',NULL,'van','SJH1234A',1000.00,8.00,20,'available',25.00,1.50,2.00,5.00,NULL,1,'2025-09-21 08:59:34','2025-09-21 08:59:34'),('DRV002','Mary Lim','+6592222222',NULL,'Team B','DL789012',NULL,'truck','SJH5678B',2000.00,15.00,50,'available',28.00,1.50,2.00,5.00,NULL,1,'2025-09-21 08:59:34','2025-09-21 08:59:34'),('DRV003','David Wong','+6593333333',NULL,'Adhoc Team','DL345678',NULL,'van','SJH9012C',1000.00,8.00,20,'available',30.00,1.50,2.00,5.00,NULL,1,'2025-09-21 08:59:34','2025-09-21 08:59:34');
/*!40000 ALTER TABLE `drivers` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `inventory`
--

LOCK TABLES `inventory` WRITE;
/*!40000 ALTER TABLE `inventory` DISABLE KEYS */;
INSERT INTO `inventory` VALUES ('1HL015009096','1HL015009 - Black / 96m','Black / 96m','General','Miscellaneous','Colour Matte Black DimensionsHandle Drill Hole Spacing: 96mmW142 x H25.6mmFeaturesEasy to installLight Weight, Easy to MaintainMaterialMetal',4.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 480.0, \"height\": null, \"length\": 480.0}','heavy_item',1,0,1,NULL,NULL,'FutureTech','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/1H015009__all_01.jpg?v=1709996548\"]','[]',1,'2025-09-22 22:29:16','2025-09-22 22:29:16'),('2007','2007',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/2007.jpg?v=1725168993\"]','[]',1,'2025-09-22 22:31:05','2025-09-22 22:31:05'),('2013','2013',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/2013.jpg?v=1725169018\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('2022','2022',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/2022.jpg?v=1725169041\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('2029','2029',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/2029.jpg?v=1725169067\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('2039','3029',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3029.jpg?v=1725168789\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('3033','3033',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3033.jpg?v=1725163469\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('3064','3064',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3064.jpg?v=1725163898\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('3065','3065',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3065.jpg?v=1725168824\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('3071','3071',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3071.jpg?v=1725164807\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('3112','3112',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3112.jpg?v=1725164507\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('3113','3113',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3113.jpg?v=1725164484\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('3117','3117',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3117.jpg?v=1725164467\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('3128','3128',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3128.jpg?v=1725163934\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('3130','3130',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3130.jpg?v=1725164440\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('3131','3131',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3131.jpg?v=1725164420\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('4018','4018',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/4018.jpg?v=1725169237\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('4019','4019',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/4019.jpg?v=1725169264\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('4046','4046',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/4046.jpg?v=1725169285\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('7657','7657',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/CS-7657-W-Marrone-Elm.jpg?v=1726925115\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('Basic/Single','5\" Stamina Foam Mattress - Basic 5\" / Single','Basic 5\" / Single','Bedroom','Mattresses','DimensionsAvailable in Single only (3\' x 6\'3)5\" thick high quality Rebond Foam Features & MaterialNon-flip design for your utmost convenienceRebond foam- more resilient than regular foamFoam and fibreFeelFirm',99.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,0,0,NULL,NULL,'Dreamland','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/products/Stamina4.jpg?v=1707900011\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/products/Stamina5.jpg?v=1707900011\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/StaminaNew2.jpg?v=1685882416\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/StaminaNew.jpg?v=1685882415\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/products/StaminaFeatures.jpg?v=1707900011\"]','[\"Mattress\"]',0,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('CU-1','Soft Close Hinge Upgrade','Upgrade / Soft Close','Hardware','Upgrades',NULL,30.00,NULL,NULL,NULL,'standard',0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-09-22 14:10:53','2025-09-22 14:10:53'),('Essential2','11\" Essential 2 Plush Top Miracoil Mattress - Essential 2 11\" / Super Single','Essential 2 11\" / Super Single','Bedroom','Mattresses','Dimensions11\" thick (27.94cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm)Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm) Features & MaterialBackcare Spring SystemPlush top cushioning for better comfort and back supportNon-flip design for your utmost convenienceIncreased spinal support & comfort with high resiliency foam cushioningFinest quilt detailingFeelFirm with Plush cushioning',529.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,0,0,NULL,NULL,'Dreamland','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop.jpg?v=1724297772\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop2.jpg?v=1724297977\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress_9846adbe-6880-4fd2-b9af-42a3b62491eb.jpg?v=1724298027\"]','[\"Mattress\"]',0,'2025-09-22 22:29:16','2025-09-22 22:29:16'),('Essential2/King','11\" Essential 2 Plush Top Miracoil Mattress - Essential 2 11\" / King','Essential 2 11\" / King','Bedroom','Mattresses','Dimensions11\" thick (27.94cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm)Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm) Features & MaterialBackcare Spring SystemPlush top cushioning for better comfort and back supportNon-flip design for your utmost convenienceIncreased spinal support & comfort with high resiliency foam cushioningFinest quilt detailingFeelFirm with Plush cushioning',759.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,0,0,NULL,NULL,'Dreamland','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop.jpg?v=1724297772\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop2.jpg?v=1724297977\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress_9846adbe-6880-4fd2-b9af-42a3b62491eb.jpg?v=1724298027\"]','[\"Mattress\"]',0,'2025-09-22 22:29:16','2025-09-22 22:29:16'),('Essential2/Queen','11\" Essential 2 Plush Top Miracoil Mattress - Essential 2 11\" / Queen','Essential 2 11\" / Queen','Bedroom','Mattresses','Dimensions11\" thick (27.94cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm)Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm) Features & MaterialBackcare Spring SystemPlush top cushioning for better comfort and back supportNon-flip design for your utmost convenienceIncreased spinal support & comfort with high resiliency foam cushioningFinest quilt detailingFeelFirm with Plush cushioning',629.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,0,0,NULL,NULL,'Dreamland','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop.jpg?v=1724297772\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop2.jpg?v=1724297977\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress_9846adbe-6880-4fd2-b9af-42a3b62491eb.jpg?v=1724298027\"]','[\"Mattress\"]',0,'2025-09-22 22:29:16','2025-09-22 22:29:16'),('Essential2/Single','11\" Essential 2 Plush Top Miracoil Mattress - Essential 2 11\" / Single','Essential 2 11\" / Single','Bedroom','Mattresses','Dimensions11\" thick (27.94cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm)Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm) Features & MaterialBackcare Spring SystemPlush top cushioning for better comfort and back supportNon-flip design for your utmost convenienceIncreased spinal support & comfort with high resiliency foam cushioningFinest quilt detailingFeelFirm with Plush cushioning',449.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,0,0,NULL,NULL,'Dreamland','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop.jpg?v=1724297772\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop2.jpg?v=1724297977\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress_9846adbe-6880-4fd2-b9af-42a3b62491eb.jpg?v=1724298027\"]','[\"Mattress\"]',0,'2025-09-22 22:29:16','2025-09-22 22:29:16'),('Essential3/King','10\" Essential 3 Miracoil Mattress - King','King','Bedroom','Mattresses','Dimensions10\" thick (25.4cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm) Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm)Features & MaterialSpring SystemNon-flip design for your utmost convenienceSuper supportive in all the right places with high resiliency foamFinest quilt detailingFeelFirm*Bed frame not included **Our standard wait time is between 3 to 7 days but we can sometimes deliver earlier if there are open slots left (P.S. We don\'t deliver on weekends and PHs). If you would like to request a specific weekday and time of delivery, there\'s a premium surcharge of $30 and $50 for self-assembled and assembled items respectively if the day\'s schedule is full. This special arrangement is subjected to availability and prices may differ during peak periods. If your apartment is not ready, we can also hold your order and deliver at a later date.**',629.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,1,0,NULL,NULL,'Dreamland',NULL,'[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Essential3Classic3NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3ClassicFeaturesNEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic4NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic2NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress.jpg?v=1721121106\"]','[\"Mattress\"]',0,'2025-09-22 22:29:16','2025-09-22 22:29:16'),('Essential3/Queen','10\" Essential 3 Miracoil Mattress - Queen','Queen','Bedroom','Mattresses','Dimensions10\" thick (25.4cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm) Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm)Features & MaterialSpring SystemNon-flip design for your utmost convenienceSuper supportive in all the right places with high resiliency foamFinest quilt detailingFeelFirm*Bed frame not included **Our standard wait time is between 3 to 7 days but we can sometimes deliver earlier if there are open slots left (P.S. We don\'t deliver on weekends and PHs). If you would like to request a specific weekday and time of delivery, there\'s a premium surcharge of $30 and $50 for self-assembled and assembled items respectively if the day\'s schedule is full. This special arrangement is subjected to availability and prices may differ during peak periods. If your apartment is not ready, we can also hold your order and deliver at a later date.**',529.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,1,0,NULL,NULL,'Dreamland',NULL,'[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Essential3Classic3NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3ClassicFeaturesNEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic4NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic2NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress.jpg?v=1721121106\"]','[\"Mattress\"]',0,'2025-09-22 22:29:16','2025-09-22 22:29:16'),('Essential3/Single','10\" Essential 3 Miracoil Mattress - Single','Single','Bedroom','Mattresses','Dimensions10\" thick (25.4cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm) Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm)Features & MaterialSpring SystemNon-flip design for your utmost convenienceSuper supportive in all the right places with high resiliency foamFinest quilt detailingFeelFirm*Bed frame not included **Our standard wait time is between 3 to 7 days but we can sometimes deliver earlier if there are open slots left (P.S. We don\'t deliver on weekends and PHs). If you would like to request a specific weekday and time of delivery, there\'s a premium surcharge of $30 and $50 for self-assembled and assembled items respectively if the day\'s schedule is full. This special arrangement is subjected to availability and prices may differ during peak periods. If your apartment is not ready, we can also hold your order and deliver at a later date.**',409.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,1,0,NULL,NULL,'Dreamland',NULL,'[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Essential3Classic3NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3ClassicFeaturesNEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic4NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic2NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress.jpg?v=1721121106\"]','[\"Mattress\"]',0,'2025-09-22 22:29:16','2025-09-22 22:29:16'),('Essential3/SuperSingle','10\" Essential 3 Miracoil Mattress - Super Single','Super Single','Bedroom','Mattresses','Dimensions10\" thick (25.4cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm) Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm)Features & MaterialSpring SystemNon-flip design for your utmost convenienceSuper supportive in all the right places with high resiliency foamFinest quilt detailingFeelFirm*Bed frame not included **Our standard wait time is between 3 to 7 days but we can sometimes deliver earlier if there are open slots left (P.S. We don\'t deliver on weekends and PHs). If you would like to request a specific weekday and time of delivery, there\'s a premium surcharge of $30 and $50 for self-assembled and assembled items respectively if the day\'s schedule is full. This special arrangement is subjected to availability and prices may differ during peak periods. If your apartment is not ready, we can also hold your order and deliver at a later date.**',439.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,1,0,NULL,NULL,'Dreamland',NULL,'[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Essential3Classic3NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3ClassicFeaturesNEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic4NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic2NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress.jpg?v=1721121106\"]','[\"Mattress\"]',0,'2025-09-22 22:29:16','2025-09-22 22:29:16'),('Extra/Single','8\" Stamina Extra Foam Mattress',NULL,'Bedroom','Mattresses','DimensionsAvailable in Single only (3\' x 6\'3)5\" thick high quality Rebond Foam Features & MaterialNon-flip design for your utmost convenienceRebond foam- more resilient than regular foamFoam and fibreTricot FabricFeelFirm',159.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,0,0,NULL,NULL,'Dreamland','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Cabana.jpg?v=1728137845\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/DreamlandRebondedOrthoMattress_1.jpg?v=1707900011\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/products/Stamina5.jpg?v=1707900011\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/products/Stamina4.jpg?v=1707900011\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/products/StaminaFeatures.jpg?v=1707900011\"]','[\"Mattress\"]',0,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('H2/8-NC','2/8\" Hinge (Curved Middle) - 2/8\" Hinge / Normal Close','2/8\" Hinge / Normal Close','General','Miscellaneous',NULL,3.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/1_4_Hinge_20230524_222411_0001.jpg?v=1684947528\"]','[]',0,'2025-09-22 22:31:05','2025-09-22 22:31:05'),('H5/8-NC','5/8\" Hinge (Flat Side) - 5/8\" Hinge / Normal Close','5/8\" Hinge / Normal Close','General','Miscellaneous',NULL,3.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/jpg_20230524_222710_0000.jpg?v=1684947306\"]','[]',0,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8047727739102_VAR_44881945297118','5/8\" Hinge (Flat Side) - 5/8\" Hinge / Soft Close','5/8\" Hinge / Soft Close','General','Miscellaneous',NULL,3.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/jpg_20230524_222710_0000.jpg?v=1684947306\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8047728492766_VAR_44881945166046','2/8\" Hinge (Curved Middle) - 2/8\" Hinge / Soft Close','2/8\" Hinge / Soft Close','General','Miscellaneous',NULL,3.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/1_4_Hinge_20230524_222411_0001.jpg?v=1684947528\"]','[]',1,'2025-09-22 22:31:05','2025-09-22 22:31:05'),('PROD_8047728689374_VAR_44881932943582','7/8\" Hinge (Curved) - 7/8\" Hinge / Normal Close','7/8\" Hinge / Normal Close','General','Miscellaneous',NULL,3.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/7_8_Hinge_20230524_222411_0002.jpg?v=1684947598\"]','[]',0,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8047728689374_VAR_44881945592030','7/8\" Hinge (Curved) - 7/8\" Hinge / Soft Close','7/8\" Hinge / Soft Close','General','Miscellaneous',NULL,3.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/7_8_Hinge_20230524_222411_0002.jpg?v=1684947598\"]','[]',0,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8311474946270_VAR_44875336122590','1HL015009 - Black / Knob','Black / Knob','General','Miscellaneous','Colour Matte Black DimensionsHandle Drill Hole Spacing: 96mmW142 x H25.6mmFeaturesEasy to installLight Weight, Easy to MaintainMaterialMetal',3.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 480.0, \"height\": null, \"length\": 480.0}','heavy_item',1,0,1,NULL,NULL,'FutureTech',NULL,'[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/1H015009__all_01.jpg?v=1709996548\"]','[]',1,'2025-09-22 22:31:05','2025-09-22 22:31:05'),('PROD_8664518721758_VAR_45853937205470','3035',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3035.jpg?v=1725163549\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8664518787294_VAR_45853937271006','3036',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3036.jpg?v=1742360086\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8664518820062_VAR_45853937336542','3044',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3044.jpg?v=1725163616\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8664518983902_VAR_45853938778334','3045',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3045.jpg?v=1725163702\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8664519114974_VAR_45853939204318','3047',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3047.jpg?v=1725163812\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8664519147742_VAR_45853939269854','3050',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3050.jpg?v=1725163841\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684252954846_VAR_45906024169694','6331',NULL,'General','Miscellaneous','12mm',0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/SHG-6331-P-Tortilla-Veneto.jpg?v=1726899163\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684253970654_VAR_45906035802334','8434',NULL,'General','Miscellaneous','8mm or 12mm',0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/NV-8434-W-Palasanto.jpg?v=1726899438\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684254724318_VAR_45906039439582','6416',NULL,'General','Miscellaneous','8mm or 12mm',0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/NV-6416-W-Mayo-Oak.jpg?v=1726899518\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684255346910_VAR_45906044354782','6400',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/CDM-6400-W-Shyam-Teak.jpg?v=1726899630\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684255576286_VAR_45906047795422','5663',NULL,'General','Miscellaneous','8mm or 12mm',0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/NV-5663-W-Corell-Walnut.jpg?v=1726899678\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684255871198_VAR_45906049564894','5661',NULL,'General','Miscellaneous','8mm or 12mm',0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/NV-5661-W-Scara-Walnut.jpg?v=1726899734\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684461555934_VAR_45906884427998','6483',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/CN-6483-P-Concrete.jpg?v=1726924584\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684461719774_VAR_45906884853982','8801',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/AF-8801-S-Onyx.jpg?v=1726924703\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684462047454_VAR_45906885640414','8803',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/AF-8803-S-Magma.jpg?v=1726924772\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684462538974_VAR_45906887442654','8806',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/AF-8806-S-Chiffon-White.jpg?v=1726924828\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684462670046_VAR_45906887868638','8807',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/AF-8807-S-Sandstone.jpg?v=1726924931\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684462899422_VAR_45906889474270','6880',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ST-6880-P-Black-Portoro.jpg?v=1726925002\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684463227102_VAR_45906890424542','5601',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/NV-5601-P-Bruno-Kamala.jpg?v=1726925387\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684463784158_VAR_45906897076446','5626',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/NV-5626-W-Cayman.jpg?v=1726925668\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('PROD_8684463849694_VAR_45906898059486','6336',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/SHG-6336-P-Black-Greystone.jpg?v=1726925717\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('SC15(X2)','Vegas Oak 90cm Wide 1.62m High Shoe Cabinet',NULL,'Storage','Cabinets',NULL,249.00,NULL,NULL,NULL,'standard',0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-09-22 14:10:53','2025-09-22 14:10:53'),('SKU001','Office Chair Model A','Standard','Furniture',NULL,NULL,199.00,12.50,0.30,NULL,'standard',0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-09-21 08:59:34','2025-09-21 08:59:34'),('SKU002','Standing Desk 120cm','Electric','Furniture',NULL,NULL,899.00,45.00,2.10,NULL,'heavy_item',1,1,0,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-09-21 08:59:34','2025-09-21 08:59:34'),('SKU003','Storage Cabinet','White','Furniture',NULL,NULL,299.00,25.00,1.50,NULL,'assembly_required',0,1,0,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-09-21 08:59:34','2025-09-21 08:59:34'),('SKU004','Glass Coffee Table','Premium','Furniture',NULL,NULL,599.00,30.00,1.20,NULL,'fragile',1,0,0,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-09-21 08:59:34','2025-09-21 08:59:34'),('SKU005','Sectional Sofa','Large','Furniture',NULL,NULL,1599.00,80.00,5.00,NULL,'white_glove',1,1,0,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-09-21 08:59:34','2025-09-21 08:59:34'),('T80','48mm OPP Tape',NULL,'General','Miscellaneous','48mm 80 yards 48 microns',2.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/opp-tape8.jpg?v=1728179267\"]','[]',1,'2025-09-22 22:31:06','2025-09-22 22:31:06'),('TEST002','Alison 52cm Maple/White Side Table',NULL,'Furniture',NULL,'Ergonomic office chair for testing purposes',199.00,15.50,0.80,'{\"unit\": \"cm\", \"depth\": 35, \"width\": 52, \"height\": 55, \"leg_height\": 15, \"additional_info\": \"with legs included\", \"raw_description\": \"W52 x D35 x H55cm with legs included (Legs H15cm)\"}','standard',0,0,0,NULL,NULL,NULL,NULL,'[]','[]',1,'2025-09-21 10:51:57','2025-09-21 10:51:57'),('TEST004','Test Office Chair',NULL,'Furniture',NULL,'Ergonomic office chair for testing purposes',299.99,15.50,0.80,'{\"unit\": \"cm\", \"depth\": 35, \"width\": 52, \"height\": 55, \"leg_height\": 15, \"additional_info\": \"with legs included\", \"raw_description\": \"W52 x D35 x H55cm with legs included (Legs H15cm)\"}','standard',0,0,0,NULL,NULL,NULL,NULL,'[]','[]',1,'2025-09-21 14:12:34','2025-09-21 14:12:34'),('Trifold','3\" Tri-fold Foam Mattress',NULL,'Bedroom','Mattresses','Dimensions3\' x 6\' / 90 x 190cmApprox 63cm x 90cm x 28cm (when folded)3\" thickFeatures & MaterialWhite knitted polyester FabricLatex-feel for comfortable sleepHigh-resiliency FoamTri-fold for portability and easy storageLong-lastingFeelMedium Firm',119.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,0,1,NULL,NULL,'Dreamland','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Tri-Fold.jpg?v=1724298821\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/products/Trifold3.jpg?v=1724298830\"]','[\"Mattress\"]',0,'2025-09-22 22:31:06','2025-09-22 22:31:06');
/*!40000 ALTER TABLE `inventory` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES ('6d8945b2-9637-4cd6-a2f6-1c8b216c420e','06881057-4189-423e-afd7-cc7668f15bfe','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-22 22:26:25'),('e85aa3c1-f67d-483f-a762-39b3fa5b139e','06881057-4189-423e-afd7-cc7668f15bfe','SC15(X2)','Vegas Oak 90cm Wide 1.62m High Shoe Cabinet',NULL,1,249.00,249.00,0,NULL,'2025-09-22 22:26:25');
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

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
  `order_date` date NOT NULL,
  `order_value` decimal(12,2) NOT NULL DEFAULT '0.00',
  `currency` varchar(3) DEFAULT 'SGD',
  `tag` varchar(100) DEFAULT NULL,
  `note` text,
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
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`) ON DELETE CASCADE,
  CONSTRAINT `chk_order_value` CHECK ((`order_value` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES ('06881057-4189-423e-afd7-cc7668f15bfe','12054','6704824615134','12054','59d67a1d-3d3d-482d-a532-94b0db80d54f','validated','2025-09-22',273.42,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-22 22:26:25','2025-09-22 22:26:25');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `routes`
--

LOCK TABLES `routes` WRITE;
/*!40000 ALTER TABLE `routes` DISABLE KEYS */;
/*!40000 ALTER TABLE `routes` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `system_events`
--

LOCK TABLES `system_events` WRITE;
/*!40000 ALTER TABLE `system_events` DISABLE KEYS */;
/*!40000 ALTER TABLE `system_events` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `user_sessions`
--

LOCK TABLES `user_sessions` WRITE;
/*!40000 ALTER TABLE `user_sessions` DISABLE KEYS */;
INSERT INTO `user_sessions` VALUES ('3589586e-3dd1-4334-b111-e214e9a20cf6','c1ad6b47-7cd5-402e-b26f-9ccf88c50fc0','pbkdf2:sha256:600000$F2DbisUk8ZJrXRKR$3e292a7de4497b762c738537afc9bc7777dfbdda5cab0d0a5503bef3c5bdc96c','2025-09-28 14:12:33','2025-09-21 14:12:33','2025-09-21 14:12:33','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36','172.18.0.1'),('8e90f9f7-fe75-4f4e-ab68-94536e67acd0','c1ad6b47-7cd5-402e-b26f-9ccf88c50fc0','pbkdf2:sha256:600000$r1VvYqF3XqEe4ESV$8a9b968c247603239e1774d3701e63add8ba3076695799e7146b4c0d77a3df37','2025-09-28 09:32:06','2025-09-21 09:32:06','2025-09-21 09:32:06','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36','172.18.0.1'),('ac6d4d75-f0df-493b-ae6e-28824f55efde','c1ad6b47-7cd5-402e-b26f-9ccf88c50fc0','pbkdf2:sha256:600000$eQBvSJqZit7jwzzE$472a86c8caf7865899e3a0a317d8a38d340a345694c373764c927ed519b97a79','2025-09-28 10:51:54','2025-09-21 10:51:53','2025-09-21 10:51:53','Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36','172.18.0.1');
/*!40000 ALTER TABLE `user_sessions` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('4b650253-96c9-11f0-86bc-d2f552c411bd','admin@levels.sg','$2b$12$example_hash_admin','admin',1,NULL,0,NULL,'2025-09-21 08:59:34','2025-09-21 08:59:34'),('4b65046f-96c9-11f0-86bc-d2f552c411bd','warehouse@levels.sg','$2b$12$example_hash_warehouse','warehouse',1,NULL,0,NULL,'2025-09-21 08:59:34','2025-09-21 08:59:34'),('4b650563-96c9-11f0-86bc-d2f552c411bd','driver1@levels.sg','$2b$12$example_hash_driver1','driver',1,NULL,0,NULL,'2025-09-21 08:59:34','2025-09-21 08:59:34'),('4b6505b2-96c9-11f0-86bc-d2f552c411bd','hq@levels.sg','$2b$12$example_hash_hq','hq',1,NULL,0,NULL,'2025-09-21 08:59:34','2025-09-21 08:59:34'),('4b6505f3-96c9-11f0-86bc-d2f552c411bd','cs@levels.sg','$2b$12$example_hash_cs','customer_service',1,NULL,0,NULL,'2025-09-21 08:59:34','2025-09-21 08:59:34'),('c1ad6b47-7cd5-402e-b26f-9ccf88c50fc0','test@levels.sg','pbkdf2:sha256:600000$MV0uvzrKsPaS8neV$bc7e332d77e336977aae1e6ba503f0ef63d15538e57c5844660e847b73ed2967','admin',1,'2025-09-21 14:12:33',0,NULL,'2025-09-21 09:32:04','2025-09-21 14:12:33');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

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
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-22 22:51:07
