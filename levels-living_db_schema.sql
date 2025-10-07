-- MySQL dump 10.13  Distrib 8.0.43, for macos15 (arm64)
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

CREATE DATABASE IF NOT EXISTS `levels_living_db_new` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `levels_living_db_new`;


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
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES ('021b122b-3cc0-4990-9679-f82b481503d6','Mui Lee Goh','+6591189396','406 Bukit Batok West Ave 7','13-36','650406','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.33750000,103.70470000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('0414bf91-0184-4ed1-92fd-1bcd54d5686a','Tan Kong Seng','+6582476955','38 Lorong 5 Toa Payoh','11-467','310038','HDB','{\"sms\": false, \"email\": false, \"phone\": true}',1.31380000,103.96480000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('0702f80a-92f1-4c29-855d-3b7b7d2f64dc','Ms Teh','93280285','119 Ho Ching Road','03-12','610119',NULL,'{\"sms\": true, \"email\": false}',1.33509910,103.72443630,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('081f485b-3f65-4166-84e4-89c7266ab49b','Serene Tan','96910323','688a Choa Chu Kang Drive','08-348','681688',NULL,'{\"sms\": true, \"email\": false}',1.40385860,103.75060840,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('0da9a3bd-2ee9-4790-94de-adde24ba5ece','Seren Nah','91874990','101 Whampoa Drive','06-172','323101',NULL,'{\"sms\": true, \"email\": false}',1.32042160,103.85382080,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('0f3428a9-9979-4e94-80eb-9e6daf4bb3f7','Mridula Murugan','+6591874117','250D Compassvale Street','05-51','544250','HDB','{\"sms\": false, \"email\": true, \"phone\": false}',1.36910000,103.84540000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('11b9a391-b826-4f78-acff-7e2728f499ed','Mustafi -','96749781','316 Ubi Avenue 1','05-365','400316',NULL,'{\"sms\": true, \"email\": false}',1.32917040,103.90258100,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('12ce1c79-6903-434e-89f9-041fb9ecea96','Hasizah -','+6582993260','926 Jurong West Street 92','05-123','640926','HDB','{\"sms\": false, \"email\": false, \"phone\": true}',1.33750000,103.70470000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('18ef083a-4dce-48f2-9e17-76b167958ae2','Eng Huat Tan','92356511','249 Bangkit Road','08-336','670249',NULL,'{\"sms\": true, \"email\": false}',1.38103820,103.77388860,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('2248d969-08aa-48a5-abdb-05e899fc1ce0','Joyce Chua','98450010','12 Jalan Bukit Merah','21-5048','150012',NULL,'{\"sms\": true, \"email\": false}',1.28745510,103.80706910,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('25936975-6862-4e08-9e86-04144a436163','Sio Yen Tan','86881514','153 Rivervale Crescent','13-112','540153',NULL,'{\"sms\": true, \"email\": false}',1.39153170,103.90653090,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('2c72c515-7c44-47d6-b41f-c5d0f79f0b6b','Efa Farzana','99397287','793 Woodlands Avenue 6','06-667','730793',NULL,'{\"sms\": true, \"email\": false}',1.44258680,103.80259640,1,'2025-09-28 09:13:11','2025-09-28 09:13:11'),('2c8aa7b2-26de-4d0b-b9c7-b495aec4502e','Abdullah -','+6587619011','38 Chai Chee Avenue','08-195','461038','HDB','{\"sms\": false, \"email\": false, \"phone\": true}',1.31620000,103.90580000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('2ec43c33-b5db-4a8d-98d1-839fc41af4d1','Jeanntte Koh','+6598472637','856D Tampines Street 82','12-186','524856','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.36910000,103.84540000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('3086de2e-1944-4ed2-89d6-5f71a323a8e3','Samuel Yong','+6594590885','11 Toh Yi Drive','03-361','590011','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.36910000,103.84540000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('31bc4b6b-7558-41a0-a864-ac7e7b81fa9f','Tan Kong Seng','82476955','38 Lorong 5 Toa Payoh','11-467','310038',NULL,'{\"sms\": true, \"email\": false}',1.33531280,103.85542040,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('331f7ff7-36b6-43da-8f75-0bb67199aeba','Eileen -','+6597462776','8 Mar Thoma Road','09-05','328689','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.31380000,103.96480000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('34bf7352-01a8-4e62-a937-6435f9ff02bd','Ms Teh','+6593280285','119 Ho Ching Road','03-12','610119','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.33750000,103.70470000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('35e690e0-a8e4-429f-8ce6-b2ec61d529e8','Jess -','+6581869904','36 Middle Road The M Condo','20-30','188945','Condo','{\"sms\": false, \"email\": true, \"phone\": true}',1.30480000,103.83180000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('372241f0-9e4d-4c2f-85e6-3885493cfae2','Eileen -','97462776','8 Mar Thoma Road','09-05','328689',NULL,'{\"sms\": true, \"email\": false}',1.32637950,103.86214330,1,'2025-09-28 09:13:11','2025-09-28 09:13:11'),('3c0f1a17-9de0-4fe0-924d-a590209aafd7','Anja Eckert','98833229','121 Bukit Batok Central','04-447','650121',NULL,'{\"sms\": true, \"email\": false}',1.35151620,103.74788880,1,'2025-09-28 09:13:11','2025-09-28 09:13:11'),('3c474180-1b64-4315-9e78-6c94186cfa8b','Serene Tan','+6596910323','688a Choa Chu Kang Drive','08-348','681688','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.33750000,103.70470000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('3d8e2de2-471a-4e7d-8fa4-26488fe40171','Alice Neo','97639813','36 Phoenix Garden',NULL,'668302',NULL,'{\"sms\": true, \"email\": false}',1.37659610,103.75944630,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('3f21fd28-8139-4005-9276-24cc13f68ad8','Linda Yip','81130979','9 Lorong 7 Toa Payoh','03-323','310009',NULL,'{\"sms\": true, \"email\": false}',1.33758820,103.85776490,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('41e61fd4-5a4d-49d8-9aac-d04df468bde3','Anja Eckert','92777768','121 Bukit Batok Central','04-447','650121','HDB','{\"sms\": false, \"email\": false, \"phone\": false}',1.33750000,103.70470000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('4489a962-f08c-4429-a94d-192df3bafb72','Samuel Yong','94590885','11 Toh Yi Drive','03-361','590011',NULL,'{\"sms\": true, \"email\": false}',1.33779790,103.77276090,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('44e692d1-4eb5-4c5c-9252-5a659a0c871b','Linda Yip','+6581130979','9 Lorong 7 Toa Payoh','03-323','310009','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.31380000,103.96480000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('4727febd-3d6b-44f3-8d37-f53a0a4213c4','Lin Hui Fang','+6587990544','19 Dunman Lane','level 2','439271','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.31620000,103.90580000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('49582f40-c641-4228-b9ad-07dc35aee847','Sabrina Yeo','+6598591030','494H Tampines Street 45','10-586','528494','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.36910000,103.84540000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('4a81545f-ad0e-410f-ae9e-1e197a848a5f','Raushan Kumar','+6593913263','Butterworth8','02-10,block 8','439423','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.31620000,103.90580000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('4ac84907-1c2c-4b85-bc8f-e51299da4474','Muhammad Firman','83394031','507A Wellington Circle','02-164','751507',NULL,'{\"sms\": true, \"email\": false}',1.45267150,103.82390870,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('4c261909-13c5-4852-8927-48e58e32f7eb','Jainah Bte Ahdim','93162288','259 Tampines Street 21','06-336','520259',NULL,'{\"sms\": true, \"email\": false}',1.35505620,103.94994960,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('4e01f27e-a5a4-4b1a-9d5a-80752a31157b','Skylar Seah','90171185','9 Boon Teck Road','05-01','329583',NULL,'{\"sms\": true, \"email\": false}',1.32676820,103.84962440,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('53f063c1-c0e8-4125-875a-0143ed9ffe87','Florence Loo','83335150','152 Toa Payoh Lorong 2','12-330','310152',NULL,'{\"sms\": true, \"email\": false}',1.33410780,103.84585510,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('559b7ba4-8e94-448e-9f54-bcac878a54f6','Mohamed Rashid B. Ibrahim','96438422','954B Tampines Street 96','09-209','522954',NULL,'{\"sms\": true, \"email\": false}',1.34228330,103.93709700,1,'2025-09-28 09:13:11','2025-09-28 09:13:11'),('57ae5266-ede9-4529-9173-9a8a299614f3','Ivy Yip','81853565','20 Jalan Haji Salam',NULL,'468790',NULL,'{\"sms\": true, \"email\": false}',1.32153850,103.95221070,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('581bd086-5518-4e04-bdb2-e6b34c40e8c7','Sabrina Yeo','98591030','494H Tampines Street 45','10-586','528494',NULL,'{\"sms\": true, \"email\": false}',1.36369380,103.95506860,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('5abf63e2-ca60-4846-b961-a41267aa4b8c','Lai Chan Lee','82631712','76 Lorong Limau','13-25','320076',NULL,'{\"sms\": true, \"email\": false}',1.32521900,103.85435590,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('609fb9a3-d60c-4b81-97c6-38db88479c14','Stella Tan','+6597895533','31 Jalan Rama Rama','25-02','329111','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.31380000,103.96480000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('63dfc571-af4e-4c1e-8ea7-695a0184c6ec','William Cheong','97803989','369 Holland Road','12-01','278640',NULL,'{\"sms\": true, \"email\": false}',1.32020660,103.78069960,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('6b0a3175-6f61-4ad4-b474-63577cd682fb','Anthony Siow','+6596311943','15 Bedok South Road','14-115','460015','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.31620000,103.90580000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('6c0d7ea8-c1d5-4d4c-b578-4703aa3b37a5','Ramli -','+6597708049','12 Loyang Besar Close','04-10','509051','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.36910000,103.84540000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('6ce81706-b88f-41a1-a502-77972faf5313','Francis Peh','84689186','141 Lorong 2 Toa Payoh','21-158','311141',NULL,'{\"sms\": true, \"email\": false}',1.33565240,103.84588090,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('6fddde78-bc78-4e9d-bf37-8c1cfd6db92a','Efa Farzana','98181724','793 Woodlands Avenue 6','06-667','730793',NULL,'{\"sms\": true, \"email\": false}',1.44258680,103.80259640,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('71b526c3-03be-4ed5-b489-0c43ca594f73','Jessie Tan','+6590666618','403B Lorong 1 Toa Payoh','18-642','312403','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.31380000,103.96480000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('71caf01f-846d-4968-b62c-b7b57634c665','Seow Chong Yeow','+6597343030','596C Ang Mo Kio Street 52','24-341','563596','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.36910000,103.84540000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('742b3d12-9d7f-40ec-9170-8619b3fff980','Lin Hui Fang','87990544','19 Dunman Lane','level 2','439271',NULL,'{\"sms\": true, \"email\": false}',1.30908490,103.89603510,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('7689ccd2-e27b-4984-916f-4820cb7ac688','Mohamed Rashid B. Ibrahim','93767475','954B Tampines Street 96','09-209','522954',NULL,'{\"sms\": true, \"email\": false}',1.34228330,103.93709700,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('77560218-a59b-4387-9d2f-47ecc5e25af1','Raushan Kumar','93913263','Butterworth8','02-10,block 8','439423',NULL,'{\"sms\": true, \"email\": false}',1.31221690,103.89511590,1,'2025-09-28 09:13:11','2025-09-28 09:13:11'),('777a19fc-0206-4ce3-911f-a87fef6db17e','Seow Chong Yeow','97343030','596C Ang Mo Kio Street 52','24-341','563596',NULL,'{\"sms\": true, \"email\": false}',1.37210870,103.85018100,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('7b6b9101-cc16-4b51-8311-6c7fee547b68','Kelvin -','96880305','53 Jalan Bunga Rampai','03-05','538421',NULL,'{\"sms\": true, \"email\": false}',1.33893740,103.88306790,1,'2025-09-28 09:13:11','2025-09-28 09:13:11'),('829b3792-16bb-4a19-8611-5f96a5d58ab2','Kelly Ang','94245287','102 Gerald Drive','01-79','798593',NULL,'{\"sms\": true, \"email\": false}',1.38819940,103.87914670,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('886c9d6d-94de-488f-80e7-f42d60a0d312','Efa Farzana','+6593355755','793 Woodlands Avenue 6','06-667','730793','HDB','{\"sms\": false, \"email\": true, \"phone\": false}',1.41840000,103.82350000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('88ae0691-7c1f-487c-ba77-71c51c487a9e','Kenny Liew','92760997','66 Marine Parade Road','21-13, Cote Dâ€™azur','449300',NULL,'{\"sms\": true, \"email\": false}',1.30051840,103.90466130,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('8caa2d78-0fc2-43c6-941c-708d64bcede6','Cindy Lee','97958844','561 Pasir Ris Street 51','07-265','510561',NULL,'{\"sms\": true, \"email\": false}',1.36703150,103.95070370,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('8db09d37-153d-419d-9057-a8f321a9d655','Boon Hong Ng','91199950','20 Brookvale Drive','08-51, KL Residences','599982',NULL,'{\"sms\": true, \"email\": false}',1.32937860,103.76983040,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('90f8d4ea-8a48-42b6-b1ed-fc4a6d34328a','Kelvin -','+6596880305','53 Jalan Bunga Rampai','03-05','538421','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.36910000,103.84540000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('937e68ac-a466-4de6-884d-a0d3dbcf8268','Cindy Lee','+6597590659','561 Pasir Ris Street 51','07-265','510561','HDB','{\"sms\": false, \"email\": true, \"phone\": false}',1.36910000,103.84540000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('94aa9789-c730-46f5-a932-b7765af8c026','Cindy Lee','93237270','561 Pasir Ris Street 51','07-265','510561',NULL,'{\"sms\": true, \"email\": false}',1.36703150,103.95070370,1,'2025-09-28 09:13:11','2025-09-28 09:13:11'),('95242365-46c3-4aa2-96ad-7e52a2866d66','Maria .','97825557','100 Whampoa Drive','14-184','320100',NULL,'{\"sms\": true, \"email\": false}',1.32078420,103.85435500,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('9674ad6d-6642-49d8-acd0-5f1d1d172507','Abdullah -','87619011','38 Chai Chee Avenue','08-195','461038',NULL,'{\"sms\": true, \"email\": false}',1.32589280,103.92568290,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('96b18842-b717-4bb3-b305-c31ab0e5374f','Baileybelly','+6598583018','36 Dover Rise','10-11','138685','HDB','{\"sms\": false, \"email\": false, \"phone\": true}',1.30480000,103.83180000,1,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('9786b85a-d297-407d-a08f-da40ee509ad9','Tokumi Shintaro','86855704','202 Kim Seng Road','36-06','239496',NULL,'{\"sms\": true, \"email\": false}',1.29573480,103.83231350,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('9998c151-d14d-42ef-850a-6a9ff3ba2674','Siew Teo',NULL,NULL,NULL,'','HDB','{\"sms\": false, \"email\": false, \"phone\": false}',1.35210000,103.81980000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('9b9fe980-9a38-49c2-ba55-394166940fa6','Mustafi -','+6596749781','316 Ubi Avenue 1','05-365','400316','HDB','{\"sms\": false, \"email\": false, \"phone\": true}',1.31620000,103.90580000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('a02708eb-26ae-466b-bbc0-4b73427dc723','Jeanntte Koh','98472637','856D Tampines Street 82','12-186','524856',NULL,'{\"sms\": true, \"email\": false}',1.35095620,103.93766880,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('a1aa9433-ebdf-4c24-a1c8-6bb091b477ac','Florence Loo','+6583335150','152 Toa Payoh Lorong 2','12-330','310152','HDB','{\"sms\": false, \"email\": false, \"phone\": true}',1.31380000,103.96480000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('a2fdff56-18c7-406e-9872-75045def36e1','Ee Hsiang Ng','99678299','110B Bidadari Park Drive','16-236','342110',NULL,'{\"sms\": true, \"email\": false}',1.33408530,103.87298320,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('a6c1c993-8cce-4d29-a331-9d1057b39686','Ramli -','97708049','12 Loyang Besar Close','04-10','509051',NULL,'{\"sms\": true, \"email\": false}',1.37811460,103.95807490,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('ab652eb1-ce11-446c-af07-0b1d8692329a','Hasizah -','82993260','926 Jurong West Street 92','05-123','640926',NULL,'{\"sms\": true, \"email\": false}',1.34049580,103.68914550,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('abf9319c-7882-48c3-aa9e-10bbe02f586f','Rachel Tan','+6583391166','785B Woodlands Rise','10-82','732785','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.41840000,103.82350000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('aec0ef35-157d-4d5d-9ed0-c47442bfd2dc','wendy Chia','98482645','526B Pasir Ris Street 51','11-523','512526',NULL,'{\"sms\": true, \"email\": false}',1.36789810,103.94704850,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('afa3e213-174b-4d94-ad57-aa5e628d93f5','Tokumi Shintaro','+6586855704','202 Kim Seng Road','36-06','239496','HDB','{\"sms\": false, \"email\": false, \"phone\": true}',1.35190000,103.74420000,1,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('b0027c65-a3e1-4804-bbc6-42e8b7086b7c','Skylar Seah','+6590171185','9 Boon Teck Road','05-01','329583','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.31380000,103.96480000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('b162dd2e-056b-4491-8669-a9c219a2b13b','William Cheong','+6597803989','369 Holland Road','12-01','278640','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.35190000,103.74420000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('b5ee10ea-3bf2-4dd0-9a8a-c9073cc5bc77','Lim Shina',NULL,NULL,NULL,'','HDB','{\"sms\": false, \"email\": false, \"phone\": false}',1.35210000,103.81980000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('b90b20be-ae8b-49ce-bda5-0ceb15b2f778','Jainah Bte Ahdim','99848992','259 Tampines Street 21','06-336','520259',NULL,'{\"sms\": true, \"email\": false}',1.35505620,103.94994960,1,'2025-09-28 09:13:11','2025-09-28 09:13:11'),('baa772e3-c848-4d5d-8d9f-146b00635aa4','Lai Chan Lee','+6582631712','76 Lorong Limau','13-25','320076','HDB','{\"sms\": true, \"email\": false, \"phone\": true}',1.31380000,103.96480000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('bb8a783f-bc0f-4600-9772-ee465965f098','Seah Kwee Khim','+6597940369','139A Lorong 1A Toa Payoh','24-42','311139','HDB','{\"sms\": false, \"email\": false, \"phone\": true}',1.31380000,103.96480000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('bbdf35c1-314b-44a9-97ac-fd217d18c48e','Wong Kim Chong','96278059','483B Yishun Avenue 6','12-905','762483',NULL,'{\"sms\": true, \"email\": false}',1.41557180,103.83940810,1,'2025-09-28 09:13:11','2025-09-28 09:13:11'),('c23b9bd8-a6f8-4a66-9fe6-ec5d53257397','wendy Chia','+6598482645','526B Pasir Ris Street 51','11-523','512526','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.36910000,103.84540000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('c3196ff2-fc62-45c4-a20c-83a89c6c9ba0','Jessie Tan','90666618','403B Lorong 1 Toa Payoh','18-642','312403',NULL,'{\"sms\": true, \"email\": false}',1.33950990,103.84367660,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('c3206384-2271-4c62-98b5-bbd2685d67e1','Kenny Liew','+6592760997','66 Marine Parade Road','21-13, Cote D’azur','449300','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.31620000,103.90580000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('c4392738-262f-4ab6-aef6-dcafe9c36afd','HK Teow',NULL,NULL,NULL,'','HDB','{\"sms\": false, \"email\": true, \"phone\": false}',1.35210000,103.81980000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('c6b1acb9-e620-4933-8afb-022b96d07985','Muhammad Firman','+6583394031','507A Wellington Circle','02-164','751507','HDB','{\"sms\": false, \"email\": false, \"phone\": true}',1.41840000,103.82350000,1,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('c8b6e3f3-6e3e-4568-8a84-f5fd0f41ed74','Wong Kim Chong','+6596278059','483B Yishun Avenue 6','12-905','762483','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.41840000,103.82350000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('d067b94e-d257-4a30-b2e5-610747f418ca','FEI LING HEE',NULL,NULL,NULL,'','HDB','{\"sms\": false, \"email\": false, \"phone\": false}',1.35210000,103.81980000,1,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('d1385ddc-2360-442d-98c0-b7ac5675563a','Joe Goh','+6597871805','5 Jurong West Avenue 5','02-05','649485','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.33750000,103.70470000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('d27a94b5-322d-4690-a571-cb69ebd47962','Ee Hsiang Ng','92128282','110B Bidadari Park Drive','16-236','342110',NULL,'{\"sms\": true, \"email\": false}',1.33408530,103.87298320,1,'2025-09-28 09:13:11','2025-09-28 09:13:11'),('d32a6793-6e56-4873-a2b4-cfee54e080e1','Anja Eckert','91218560','121 Bukit Batok Central','04-447','650121',NULL,'{\"sms\": true, \"email\": false}',1.35151620,103.74788880,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('d4ca3fe8-5c6e-4b84-917f-48a59f6d2fb3','William Soh','+6592994465','30 Jalan Bahagia','10-376','320030','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.31380000,103.96480000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('d7c8ee77-74d6-4c26-99b6-ec3759510293','Jess -','81869904','36 Middle Road The M Condo','20-30','188945',NULL,'{\"sms\": true, \"email\": false}',1.29753620,103.85572750,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('daf04ee6-1576-414d-981b-a11a9add4399','Bren Joy','+6583466164','04-13','Block 102 jalan raja','321102','HDB','{\"sms\": false, \"email\": false, \"phone\": true}',1.31380000,103.96480000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('e1c6c40e-d6a1-4bd4-9a45-40ab8cc51ff1','Gary Lim','98246535','875 Tampines Street 84','09-20','520875',NULL,'{\"sms\": true, \"email\": false}',1.35267690,103.93193680,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('e244059a-df0e-4c62-a5ed-94eeb9637fce','Lang Khoon Lom','+6592354492','109 06-13 Whampoa Rd',NULL,'321109','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.31380000,103.96480000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('e2ebe934-fabd-4c6d-a1e5-b9ee8ac30e6b','Gary Lim','+6598246535','875 Tampines Street 84','09-20','520875','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.36910000,103.84540000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('e7d2ff8c-43a2-4b08-96bb-b581a4b15aca','Joe Goh','97871805','5 Jurong West Avenue 5','02-05','649485',NULL,'{\"sms\": true, \"email\": false}',1.34972090,103.70306320,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('e908f751-56f1-4762-99ae-bef810314393','Ivy Yip','+6581853565','20 Jalan Haji Salam',NULL,'468790','HDB','{\"sms\": false, \"email\": false, \"phone\": true}',1.31620000,103.90580000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('e9fd2679-ad74-4607-af2a-cd3872dbd3ad','Anthony Siow','96311943','15 Bedok South Road','14-115','460015',NULL,'{\"sms\": true, \"email\": false}',1.32086470,103.93556220,1,'2025-09-28 09:13:11','2025-09-28 09:13:11'),('ee9e24c8-6185-4705-a9d4-dd418de8c03f','Kelly Ang','+6594245287','102 Gerald Drive','01-79','798593','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.41840000,103.82350000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('f3712ba5-de08-4d89-94ac-5a99b5a0cfd2','Francis Peh','+6584689186','141 Lorong 2 Toa Payoh','21-158','311141','HDB','{\"sms\": false, \"email\": true, \"phone\": true}',1.31380000,103.96480000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('f71e927a-4961-43e4-b384-a6add1df4a67','Seah Kwee Khim','97940369','139A Lorong 1A Toa Payoh','24-42','311139',NULL,'{\"sms\": true, \"email\": false}',1.33632360,103.84390850,1,'2025-09-28 08:52:02','2025-09-28 08:52:02'),('f9317c4c-9773-4df1-b270-1f1267a041a9','Boon Hong Ng','+6591199950','20 Brookvale Drive','08-51','599982','HDB','{\"sms\": true, \"email\": true, \"phone\": true}',1.36910000,103.84540000,0,'2025-09-28 08:50:44','2025-09-28 08:50:44'),('user1','Testing1','+6598765432','456 Orchard Road','#05-67','238123','Condo','{\"sms\": true, \"email\": false}',1.30480000,103.81980000,1,'2025-09-20 16:59:34','2025-09-20 16:59:34'),('user2','Testing 2','+6587654321','789 Bukit Timah Road','House 1','259012','Landed','{\"sms\": true, \"email\": false}',1.33870000,103.78900000,1,'2025-09-20 16:59:34','2025-09-20 16:59:34'),('user3','Testing 3','+6591234567','123 Ang Mo Kio Avenue 1','05-365','123456','HDB','{\"sms\": false, \"email\": false, \"phone\": true, \"language\": \"en\", \"preferred_time\": \"business_hours\"}',1.30480000,103.83180000,0,'2025-09-22 06:23:48','2025-09-22 06:23:48');
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
  `route_polyline` text COMMENT 'Google Maps polyline for route visualization',
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
-- Dumping data for table `delivery_schedules`
--

LOCK TABLES `delivery_schedules` WRITE;
/*!40000 ALTER TABLE `delivery_schedules` DISABLE KEYS */;
INSERT INTO `delivery_schedules` (`schedule_id`, `schedule_date`, `driver_id`, `team`, `route_id`, `total_locations`, `max_locations`, `status`, `start_time`, `estimated_end_time`, `actual_end_time`, `route_polyline`, `total_distance_meters`, `total_duration_seconds`, `notes`, `created_by`, `created_at`, `updated_at`) VALUES ('21fa0388-66c4-4c0b-b9f5-f4473c5afd82','2025-10-06',NULL,NULL,NULL,5,18,'draft','09:00:00',NULL,NULL,NULL,NULL,NULL,NULL,'6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:04:36','2025-09-30 06:04:36'),('d9a35112-4a5c-47bb-ba1e-3acd712444e1','2025-10-03',NULL,NULL,NULL,18,18,'draft','09:00:00',NULL,NULL,NULL,NULL,NULL,NULL,'6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54','2025-09-30 06:01:54');
/*!40000 ALTER TABLE `delivery_schedules` ENABLE KEYS */;
UNLOCK TABLES;

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
INSERT INTO `drivers` VALUES ('DRV001','John Tan','+6591111111',NULL,'Team A','DL123456',NULL,'van','SJH1234A',1000.00,8.00,20,'available',25.00,1.50,2.00,5.00,NULL,1,'2025-09-20 16:59:34','2025-09-20 16:59:34'),('DRV002','Mary Lim','+6592222222',NULL,'Team B','DL789012',NULL,'truck','SJH5678B',2000.00,15.00,50,'available',28.00,1.50,2.00,5.00,NULL,1,'2025-09-20 16:59:34','2025-09-20 16:59:34'),('DRV003','David Wong','+6593333333',NULL,'Adhoc Team','DL345678',NULL,'van','SJH9012C',1000.00,8.00,20,'available',30.00,1.50,2.00,5.00,NULL,1,'2025-09-20 16:59:34','2025-09-20 16:59:34');
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
INSERT INTO `inventory` VALUES ('1HL015009096','1HL015009 - Black / 96m','Black / 96m','General','Miscellaneous','Colour Matte Black DimensionsHandle Drill Hole Spacing: 96mmW142 x H25.6mmFeaturesEasy to installLight Weight, Easy to MaintainMaterialMetal',4.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 480.0, \"height\": null, \"length\": 480.0}','heavy_item',1,0,1,NULL,NULL,'FutureTech','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/1H015009__all_01.jpg?v=1709996548\"]','[]',1,'2025-09-22 06:29:16','2025-09-22 06:29:16'),('2007','2007',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/2007.jpg?v=1725168993\"]','[]',1,'2025-09-22 06:31:05','2025-09-22 06:31:05'),('2013','2013',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/2013.jpg?v=1725169018\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('2022','2022',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/2022.jpg?v=1725169041\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('2029','2029',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/2029.jpg?v=1725169067\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('2039','3029',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3029.jpg?v=1725168789\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('3033','3033',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3033.jpg?v=1725163469\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('3064','3064',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3064.jpg?v=1725163898\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('3065','3065',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3065.jpg?v=1725168824\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('3071','3071',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3071.jpg?v=1725164807\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('3112','3112',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3112.jpg?v=1725164507\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('3113','3113',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3113.jpg?v=1725164484\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('3117','3117',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3117.jpg?v=1725164467\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('3128','3128',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3128.jpg?v=1725163934\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('3130','3130',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3130.jpg?v=1725164440\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('3131','3131',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3131.jpg?v=1725164420\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('4018','4018',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/4018.jpg?v=1725169237\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('4019','4019',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/4019.jpg?v=1725169264\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('4046','4046',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/4046.jpg?v=1725169285\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('7657','7657',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/CS-7657-W-Marrone-Elm.jpg?v=1726925115\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('Basic/Single','5\" Stamina Foam Mattress - Basic 5\" / Single','Basic 5\" / Single','Bedroom','Mattresses','DimensionsAvailable in Single only (3\' x 6\'3)5\" thick high quality Rebond Foam Features & MaterialNon-flip design for your utmost convenienceRebond foam- more resilient than regular foamFoam and fibreFeelFirm',99.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,0,0,NULL,NULL,'Dreamland','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/products/Stamina4.jpg?v=1707900011\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/products/Stamina5.jpg?v=1707900011\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/StaminaNew2.jpg?v=1685882416\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/StaminaNew.jpg?v=1685882415\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/products/StaminaFeatures.jpg?v=1707900011\"]','[\"Mattress\"]',0,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('BT4550/3101','Cubo 45cm Ash/White Bedside Table',NULL,'Furniture','General','Product: Cubo 45cm Ash/White Bedside Table',199.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 45.0, \"height\": 50.0, \"length\": 40.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('CH-1','Handle Upgrade',NULL,'Hardware','Upgrades','Product: Handle Upgrade',10.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-09-28 01:12:28'),('CTMCOLOR','Custom Furniture',NULL,'Furniture','General','Product: Custom Furniture',999.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-09-28 01:12:28'),('CTMFULL','Custom Furniture',NULL,'Furniture','General','Product: Custom Furniture',999.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-09-28 01:12:28'),('CU-1','Soft Close Hinge Upgrade','Upgrade / Soft Close','Hardware','Upgrades',NULL,30.00,NULL,NULL,NULL,'standard',0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-09-21 22:10:53','2025-09-21 22:10:53'),('Essential2','11\" Essential 2 Plush Top Miracoil Mattress - Essential 2 11\" / Super Single','Essential 2 11\" / Super Single','Bedroom','Mattresses','Dimensions11\" thick (27.94cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm)Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm) Features & MaterialBackcare Spring SystemPlush top cushioning for better comfort and back supportNon-flip design for your utmost convenienceIncreased spinal support & comfort with high resiliency foam cushioningFinest quilt detailingFeelFirm with Plush cushioning',529.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,0,0,NULL,NULL,'Dreamland','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop.jpg?v=1724297772\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop2.jpg?v=1724297977\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress_9846adbe-6880-4fd2-b9af-42a3b62491eb.jpg?v=1724298027\"]','[\"Mattress\"]',0,'2025-09-22 06:29:16','2025-09-22 06:29:16'),('Essential2/King','11\" Essential 2 Plush Top Miracoil Mattress - Essential 2 11\" / King','Essential 2 11\" / King','Bedroom','Mattresses','Dimensions11\" thick (27.94cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm)Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm) Features & MaterialBackcare Spring SystemPlush top cushioning for better comfort and back supportNon-flip design for your utmost convenienceIncreased spinal support & comfort with high resiliency foam cushioningFinest quilt detailingFeelFirm with Plush cushioning',759.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,0,0,NULL,NULL,'Dreamland','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop.jpg?v=1724297772\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop2.jpg?v=1724297977\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress_9846adbe-6880-4fd2-b9af-42a3b62491eb.jpg?v=1724298027\"]','[\"Mattress\"]',0,'2025-09-22 06:29:16','2025-09-22 06:29:16'),('Essential2/Queen','11\" Essential 2 Plush Top Miracoil Mattress - Essential 2 11\" / Queen','Essential 2 11\" / Queen','Bedroom','Mattresses','Dimensions11\" thick (27.94cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm)Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm) Features & MaterialBackcare Spring SystemPlush top cushioning for better comfort and back supportNon-flip design for your utmost convenienceIncreased spinal support & comfort with high resiliency foam cushioningFinest quilt detailingFeelFirm with Plush cushioning',629.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,0,0,NULL,NULL,'Dreamland','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop.jpg?v=1724297772\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop2.jpg?v=1724297977\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress_9846adbe-6880-4fd2-b9af-42a3b62491eb.jpg?v=1724298027\"]','[\"Mattress\"]',0,'2025-09-22 06:29:16','2025-09-22 06:29:16'),('Essential2/Single','11\" Essential 2 Plush Top Miracoil Mattress - Essential 2 11\" / Single','Essential 2 11\" / Single','Bedroom','Mattresses','Dimensions11\" thick (27.94cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm)Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm) Features & MaterialBackcare Spring SystemPlush top cushioning for better comfort and back supportNon-flip design for your utmost convenienceIncreased spinal support & comfort with high resiliency foam cushioningFinest quilt detailingFeelFirm with Plush cushioning',449.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,0,0,NULL,NULL,'Dreamland','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop.jpg?v=1724297772\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential2PlushTop2.jpg?v=1724297977\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress_9846adbe-6880-4fd2-b9af-42a3b62491eb.jpg?v=1724298027\"]','[\"Mattress\"]',0,'2025-09-22 06:29:16','2025-09-22 06:29:16'),('Essential3/King','10\" Essential 3 Miracoil Mattress - King','King','Bedroom','Mattresses','Dimensions10\" thick (25.4cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm) Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm)Features & MaterialSpring SystemNon-flip design for your utmost convenienceSuper supportive in all the right places with high resiliency foamFinest quilt detailingFeelFirm*Bed frame not included **Our standard wait time is between 3 to 7 days but we can sometimes deliver earlier if there are open slots left (P.S. We don\'t deliver on weekends and PHs). If you would like to request a specific weekday and time of delivery, there\'s a premium surcharge of $30 and $50 for self-assembled and assembled items respectively if the day\'s schedule is full. This special arrangement is subjected to availability and prices may differ during peak periods. If your apartment is not ready, we can also hold your order and deliver at a later date.**',629.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,1,0,NULL,NULL,'Dreamland',NULL,'[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Essential3Classic3NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3ClassicFeaturesNEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic4NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic2NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress.jpg?v=1721121106\"]','[\"Mattress\"]',0,'2025-09-22 06:29:16','2025-09-22 06:29:16'),('Essential3/Queen','10\" Essential 3 Miracoil Mattress - Queen','Queen','Bedroom','Mattresses','Dimensions10\" thick (25.4cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm) Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm)Features & MaterialSpring SystemNon-flip design for your utmost convenienceSuper supportive in all the right places with high resiliency foamFinest quilt detailingFeelFirm*Bed frame not included **Our standard wait time is between 3 to 7 days but we can sometimes deliver earlier if there are open slots left (P.S. We don\'t deliver on weekends and PHs). If you would like to request a specific weekday and time of delivery, there\'s a premium surcharge of $30 and $50 for self-assembled and assembled items respectively if the day\'s schedule is full. This special arrangement is subjected to availability and prices may differ during peak periods. If your apartment is not ready, we can also hold your order and deliver at a later date.**',529.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,1,0,NULL,NULL,'Dreamland',NULL,'[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Essential3Classic3NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3ClassicFeaturesNEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic4NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic2NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress.jpg?v=1721121106\"]','[\"Mattress\"]',0,'2025-09-22 06:29:16','2025-09-22 06:29:16'),('Essential3/Single','10\" Essential 3 Miracoil Mattress - Single','Single','Bedroom','Mattresses','Dimensions10\" thick (25.4cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm) Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm)Features & MaterialSpring SystemNon-flip design for your utmost convenienceSuper supportive in all the right places with high resiliency foamFinest quilt detailingFeelFirm*Bed frame not included **Our standard wait time is between 3 to 7 days but we can sometimes deliver earlier if there are open slots left (P.S. We don\'t deliver on weekends and PHs). If you would like to request a specific weekday and time of delivery, there\'s a premium surcharge of $30 and $50 for self-assembled and assembled items respectively if the day\'s schedule is full. This special arrangement is subjected to availability and prices may differ during peak periods. If your apartment is not ready, we can also hold your order and deliver at a later date.**',409.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,1,0,NULL,NULL,'Dreamland',NULL,'[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Essential3Classic3NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3ClassicFeaturesNEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic4NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic2NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress.jpg?v=1721121106\"]','[\"Mattress\"]',0,'2025-09-22 06:29:16','2025-09-22 06:29:16'),('Essential3/SuperSingle','10\" Essential 3 Miracoil Mattress - Super Single','Super Single','Bedroom','Mattresses','Dimensions10\" thick (25.4cm)Single 3\' x 6\'3 (approx 91.44 x 190.5cm)Super Single 3\'6 x 6\'3 (approx 106.68 x 190.5cm) Queen 5\' x 6\'3 (approx 152 x 190.5cm)King 6\' x 6\'3 (approx 182.88 x 190.5cm)Features & MaterialSpring SystemNon-flip design for your utmost convenienceSuper supportive in all the right places with high resiliency foamFinest quilt detailingFeelFirm*Bed frame not included **Our standard wait time is between 3 to 7 days but we can sometimes deliver earlier if there are open slots left (P.S. We don\'t deliver on weekends and PHs). If you would like to request a specific weekday and time of delivery, there\'s a premium surcharge of $30 and $50 for self-assembled and assembled items respectively if the day\'s schedule is full. This special arrangement is subjected to availability and prices may differ during peak periods. If your apartment is not ready, we can also hold your order and deliver at a later date.**',439.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,1,0,NULL,NULL,'Dreamland',NULL,'[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Essential3Classic3NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3ClassicFeaturesNEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic4NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ChiroEssential3Classic2NEW.jpg?v=1721120420\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Springmattress.jpg?v=1721121106\"]','[\"Mattress\"]',0,'2025-09-22 06:29:16','2025-09-22 06:29:16'),('Extra/Single','8\" Stamina Extra Foam Mattress',NULL,'Bedroom','Mattresses','DimensionsAvailable in Single only (3\' x 6\'3)5\" thick high quality Rebond Foam Features & MaterialNon-flip design for your utmost convenienceRebond foam- more resilient than regular foamFoam and fibreTricot FabricFeelFirm',159.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,0,0,NULL,NULL,'Dreamland','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Cabana.jpg?v=1728137845\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/DreamlandRebondedOrthoMattress_1.jpg?v=1707900011\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/products/Stamina5.jpg?v=1707900011\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/products/Stamina4.jpg?v=1707900011\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/products/StaminaFeatures.jpg?v=1707900011\"]','[\"Mattress\"]',0,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('H2/8-NC','2/8\" Hinge (Curved Middle) - 2/8\" Hinge / Normal Close','2/8\" Hinge / Normal Close','General','Miscellaneous',NULL,3.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/1_4_Hinge_20230524_222411_0001.jpg?v=1684947528\"]','[]',0,'2025-09-22 06:31:05','2025-09-22 06:31:05'),('H5/8-NC','5/8\" Hinge (Flat Side) - 5/8\" Hinge / Normal Close','5/8\" Hinge / Normal Close','General','Miscellaneous',NULL,3.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/jpg_20230524_222710_0000.jpg?v=1684947306\"]','[]',0,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8047727739102_VAR_44881945297118','5/8\" Hinge (Flat Side) - 5/8\" Hinge / Soft Close','5/8\" Hinge / Soft Close','General','Miscellaneous',NULL,3.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/jpg_20230524_222710_0000.jpg?v=1684947306\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8047728492766_VAR_44881945166046','2/8\" Hinge (Curved Middle) - 2/8\" Hinge / Soft Close','2/8\" Hinge / Soft Close','General','Miscellaneous',NULL,3.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/1_4_Hinge_20230524_222411_0001.jpg?v=1684947528\"]','[]',1,'2025-09-22 06:31:05','2025-09-22 06:31:05'),('PROD_8047728689374_VAR_44881932943582','7/8\" Hinge (Curved) - 7/8\" Hinge / Normal Close','7/8\" Hinge / Normal Close','General','Miscellaneous',NULL,3.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/7_8_Hinge_20230524_222411_0002.jpg?v=1684947598\"]','[]',0,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8047728689374_VAR_44881945592030','7/8\" Hinge (Curved) - 7/8\" Hinge / Soft Close','7/8\" Hinge / Soft Close','General','Miscellaneous',NULL,3.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/7_8_Hinge_20230524_222411_0002.jpg?v=1684947598\"]','[]',0,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8311474946270_VAR_44875336122590','1HL015009 - Black / Knob','Black / Knob','General','Miscellaneous','Colour Matte Black DimensionsHandle Drill Hole Spacing: 96mmW142 x H25.6mmFeaturesEasy to installLight Weight, Easy to MaintainMaterialMetal',3.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 480.0, \"height\": null, \"length\": 480.0}','heavy_item',1,0,1,NULL,NULL,'FutureTech',NULL,'[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/1H015009__all_01.jpg?v=1709996548\"]','[]',1,'2025-09-22 06:31:05','2025-09-22 06:31:05'),('PROD_8664518721758_VAR_45853937205470','3035',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3035.jpg?v=1725163549\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8664518787294_VAR_45853937271006','3036',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3036.jpg?v=1742360086\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8664518820062_VAR_45853937336542','3044',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3044.jpg?v=1725163616\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8664518983902_VAR_45853938778334','3045',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3045.jpg?v=1725163702\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8664519114974_VAR_45853939204318','3047',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3047.jpg?v=1725163812\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8664519147742_VAR_45853939269854','3050',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/3050.jpg?v=1725163841\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684252954846_VAR_45906024169694','6331',NULL,'General','Miscellaneous','12mm',0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/SHG-6331-P-Tortilla-Veneto.jpg?v=1726899163\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684253970654_VAR_45906035802334','8434',NULL,'General','Miscellaneous','8mm or 12mm',0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/NV-8434-W-Palasanto.jpg?v=1726899438\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684254724318_VAR_45906039439582','6416',NULL,'General','Miscellaneous','8mm or 12mm',0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/NV-6416-W-Mayo-Oak.jpg?v=1726899518\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684255346910_VAR_45906044354782','6400',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/CDM-6400-W-Shyam-Teak.jpg?v=1726899630\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684255576286_VAR_45906047795422','5663',NULL,'General','Miscellaneous','8mm or 12mm',0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/NV-5663-W-Corell-Walnut.jpg?v=1726899678\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684255871198_VAR_45906049564894','5661',NULL,'General','Miscellaneous','8mm or 12mm',0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/NV-5661-W-Scara-Walnut.jpg?v=1726899734\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684461555934_VAR_45906884427998','6483',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/CN-6483-P-Concrete.jpg?v=1726924584\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684461719774_VAR_45906884853982','8801',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/AF-8801-S-Onyx.jpg?v=1726924703\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684462047454_VAR_45906885640414','8803',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/AF-8803-S-Magma.jpg?v=1726924772\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684462538974_VAR_45906887442654','8806',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/AF-8806-S-Chiffon-White.jpg?v=1726924828\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684462670046_VAR_45906887868638','8807',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/AF-8807-S-Sandstone.jpg?v=1726924931\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684462899422_VAR_45906889474270','6880',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/ST-6880-P-Black-Portoro.jpg?v=1726925002\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684463227102_VAR_45906890424542','5601',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/NV-5601-P-Bruno-Kamala.jpg?v=1726925387\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684463784158_VAR_45906897076446','5626',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/NV-5626-W-Cayman.jpg?v=1726925668\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('PROD_8684463849694_VAR_45906898059486','6336',NULL,'General','Miscellaneous',NULL,0.00,NULL,NULL,NULL,'standard',0,0,1,NULL,NULL,'Levels Living','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/SHG-6336-P-Black-Greystone.jpg?v=1726925717\"]','[]',1,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('SB1048/3075','Vernetta 100cm Walnut Sliding Shoe Bench with Cushion',NULL,'Furniture','General','Product: Vernetta 100cm Walnut Sliding Shoe Bench with Cushion',299.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": 48.0, \"length\": 40.0}','standard',0,0,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SB1204/3045-AD','Osaka 1.2m Maple XL Shoe Cabinet',NULL,'Furniture','General','Product: Osaka 1.2m Maple XL Shoe Cabinet',699.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 120.0, \"height\": 180.0, \"length\": 35.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SB1283/3075-AD','Richmond 1.2m Walnut Shoe Cabinet',NULL,'Furniture','General','Product: Richmond 1.2m Walnut Shoe Cabinet',299.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 120.0, \"height\": 100.0, \"length\": 36.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SB4311/3045WH-AD','Eden 35cm Maple/White Slim Shoe Cabinet',NULL,'Furniture','General','Product: Eden 35cm Maple/White Slim Shoe Cabinet',259.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 35.0, \"height\": 100.0, \"length\": 35.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SB8083/4049','Richie 80cm Shoe Cabinet',NULL,'Furniture','General','Product: Richie 80cm Shoe Cabinet',299.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 80.0, \"height\": 87.0, \"length\": 35.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SC15','Vegas 90cm Oak Shoe Cabinet',NULL,'Furniture','General','Product: Vegas 90cm Oak Shoe Cabinet',149.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 90.0, \"height\": 86.0, \"length\": 32.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SC15(X2)','Vegas Oak 90cm Wide 1.62m High Shoe Cabinet',NULL,'Storage','Cabinets',NULL,249.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 90.0, \"height\": 162.0, \"length\": 32.0}','standard',0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-09-21 22:10:53','2025-10-02 11:16:22'),('SC15(X2)/WAL','Vegas Walnut 90cm Wide 1.62cm High Shoe Cabinet',NULL,'Furniture','General','Product: Vegas Walnut 90cm Wide 1.62cm High Shoe Cabinet',249.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 90.0, \"height\": 162.0, \"length\": 32.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SC15/WAL','Vegas 90cm Walnut Shoe Cabinet',NULL,'Furniture','General','Product: Vegas 90cm Walnut Shoe Cabinet',149.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 90.0, \"height\": 86.0, \"length\": 32.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SC18(X2)/WAL','Texas Walnut 1.2m Wide 1.63m High Shoe Cabinet',NULL,'Furniture','General','Product: Texas Walnut 1.2m Wide 1.63m High Shoe Cabinet',299.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 120.0, \"height\": 163.0, \"length\": 32.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SC18/OAK','Texas 1.2m Oak Shoe Cabinet',NULL,'Furniture','General','Product: Texas 1.2m Oak Shoe Cabinet',169.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 120.0, \"height\": 86.5, \"length\": 32.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SC18/WAL','Texas 1.2m Walnut Shoe Cabinet',NULL,'Furniture','General','Product: Texas 1.2m Walnut Shoe Cabinet',169.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 120.0, \"height\": 86.5, \"length\": 32.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SC4','Vegas 60cm Oak Shoe Cabinet',NULL,'Furniture','General','Product: Vegas 60cm Oak Shoe Cabinet',119.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 60.0, \"height\": 86.0, \"length\": 32.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SC4/WAL','Vegas 60cm Walnut 2-Door Shoe Cabinet',NULL,'Furniture','General','Product: Vegas 60cm Walnut 2-Door Shoe Cabinet',119.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 60.0, \"height\": 86.0, \"length\": 32.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SC5','Vegas 1.2m Oak Shoe Cabinet',NULL,'Furniture','General','Product: Vegas 1.2m Oak Shoe Cabinet',169.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 60.0, \"height\": 86.0, \"length\": 32.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SC5(X2)','Vegas Oak 1.2m Wide 1.62m High Shoe Cabinet',NULL,'Furniture','General','Product: Vegas Oak 1.2m Wide 1.62m High Shoe Cabinet',299.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 120.0, \"height\": 162.0, \"length\": 32.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SC5/WAL','Vegas 1.2m Walnut 4-Door Shoe Cabinet',NULL,'Furniture','General','Product: Vegas 1.2m Walnut 4-Door Shoe Cabinet',169.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 120.0, \"height\": 86.0, \"length\": 32.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SI1295/3036-AD','Manhattan 1.2m Pine Flat Top Sideboard',NULL,'Furniture','General','Product: Manhattan 1.2m Pine Flat Top Sideboard',329.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 120.0, \"height\": 90.0, \"length\": 40.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SI1685/3045-AD','Monaco 1.6m Maple 4-Door Sideboard',NULL,'Furniture','General','Product: Monaco 1.6m Maple 4-Door Sideboard',359.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 160.0, \"height\": 95.0, \"length\": 40.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SI1685/3075-AD','Monaco 1.6m Walnut 4-Door Sideboard',NULL,'Furniture','General','Product: Monaco 1.6m Walnut 4-Door Sideboard',359.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 160.0, \"height\": 95.0, \"length\": 40.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SR4/3075-AD','Munich 1.2m Walnut Highboard Storage Cabinet',NULL,'Furniture','General','Product: Munich 1.2m Walnut Highboard Storage Cabinet',399.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 120.0, \"height\": 37.0, \"length\": 40.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SR5/3036WH','Hamburg 1.2m Pine/White Sideboard',NULL,'Furniture','General','Product: Hamburg 1.2m Pine/White Sideboard',299.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 120.0, \"height\": 79.0, \"length\": 40.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SR5/3075(Premium)','Hamburg 1.2m Walnut Sideboard',NULL,'Furniture','General','Product: Hamburg 1.2m Walnut Sideboard',299.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 120.0, \"height\": 79.0, \"length\": 40.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SR6/3036WH-AD','Hamburg 1.4m Pine/White Sideboard',NULL,'Furniture','General','Product: Hamburg 1.4m Pine/White Sideboard',329.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 140.0, \"height\": 79.0, \"length\": 40.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SR7/3036(Premium)-AD','Hamburg 1.6m Pine Sideboard',NULL,'Furniture','General','Product: Hamburg 1.6m Pine Sideboard',369.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 140.0, \"height\": 79.0, \"length\": 40.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SR7/3045WH(Premium)-AD','Hamburg 1.6m Maple/White Sideboard',NULL,'Furniture','General','Product: Hamburg 1.6m Maple/White Sideboard',369.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 160.0, \"height\": 79.0, \"length\": 40.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('SS6020/3075','Oxford 60cm Walnut Bookcase',NULL,'Furniture','General','Product: Oxford 60cm Walnut Bookcase',299.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 160.0, \"height\": 79.0, \"length\": 40.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('T1013','Pixel 5-Drawer Desk',NULL,'Furniture','General','Product: Pixel 5-Drawer Desk',399.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": 75.0, \"length\": 55.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('TEST002','Alison 52cm Maple/White Side Table',NULL,'Furniture',NULL,'Ergonomic office chair for testing purposes',199.00,15.50,0.80,'{\"unit\": \"cm\", \"depth\": 35, \"width\": 52, \"height\": 55, \"leg_height\": 15, \"additional_info\": \"with legs included\", \"raw_description\": \"W52 x D35 x H55cm with legs included (Legs H15cm)\"}','standard',0,0,0,NULL,NULL,NULL,NULL,'[]','[]',1,'2025-09-20 18:51:57','2025-09-20 18:51:57'),('TEST004','Test Office Chair',NULL,'Furniture',NULL,'Ergonomic office chair for testing purposes',299.99,15.50,0.80,'{\"unit\": \"cm\", \"depth\": 35, \"width\": 52, \"height\": 55, \"leg_height\": 15, \"additional_info\": \"with legs included\", \"raw_description\": \"W52 x D35 x H55cm with legs included (Legs H15cm)\"}','standard',0,0,0,NULL,NULL,NULL,NULL,'[]','[]',1,'2025-09-20 22:12:34','2025-09-20 22:12:34'),('Trifold','3\" Tri-fold Foam Mattress',NULL,'Bedroom','Mattresses','Dimensions3\' x 6\' / 90 x 190cmApprox 63cm x 90cm x 28cm (when folded)3\" thickFeatures & MaterialWhite knitted polyester FabricLatex-feel for comfortable sleepHigh-resiliency FoamTri-fold for portability and easy storageLong-lastingFeelMedium Firm',119.00,1000.00,NULL,'{\"unit\": \"cm\", \"width\": 100.0, \"height\": null, \"length\": 100.0}','heavy_item',1,0,1,NULL,NULL,'Dreamland','','[\"https://cdn.shopify.com/s/files/1/0630/0958/7422/files/Tri-Fold.jpg?v=1724298821\", \"https://cdn.shopify.com/s/files/1/0630/0958/7422/products/Trifold3.jpg?v=1724298830\"]','[\"Mattress\"]',0,'2025-09-22 06:31:06','2025-09-22 06:31:06'),('TV1634/3018-AD','Paisley 1.6m Oak TV Console Cabinet',NULL,'Furniture','General','Product: Paisley 1.6m Oak TV Console Cabinet',269.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 160.0, \"height\": 50.0, \"length\": 40.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('TV24/1.6/3075-AD','Hamburg 1.6m Walnut TV Console Cabinet',NULL,'Furniture','General','Product: Hamburg 1.6m Walnut TV Console Cabinet',269.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 160.0, \"height\": 54.0, \"length\": 40.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22'),('WD8003/3036-AD','Vela 80cm Modular Wardrobe',NULL,'Furniture','General','Product: Vela 80cm Modular Wardrobe',459.00,NULL,NULL,'{\"unit\": \"cm\", \"width\": 80.0, \"height\": 200.0, \"length\": 55.0}','assembly_required',1,1,1,NULL,NULL,'Levels Living',NULL,NULL,NULL,1,'2025-09-28 08:56:24','2025-10-02 11:16:22');
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
INSERT INTO `order_items` VALUES ('01636f1c-63ad-4700-9c51-97758f9a0ba9','94b75872-762a-469a-b8a8-f6d5f213fa39','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('031d87e6-e1f0-4151-83d8-f35e2f6310df','d7ec5eb9-c1a4-4ffb-8268-01fa708c7818','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('04f31f38-45c7-4218-b8f2-9ad9c583061a','3108915d-c558-4ec0-bee6-6f35e908a7fd','SC18(X2)/WAL','Texas Walnut 1.2m Wide 1.63m High Shoe Cabinet',NULL,1,299.00,299.00,0,NULL,'2025-09-28 09:13:11'),('05e5cb97-4ca0-459d-9696-55b8b9219c68','077da055-a11a-4307-8731-7937cb05e47a','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('071f1abe-9444-42e8-b469-c4ae609586c3','077da055-a11a-4307-8731-7937cb05e47a','SC18/WAL','Texas 1.2m Walnut Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('0764732d-3489-44b7-bc17-f9af3a9b6900','a9175b35-fafa-4844-9b52-a7426e1f81bd','SC15(X2)','Vegas Oak 90cm Wide 1.62m High Shoe Cabinet',NULL,1,249.00,249.00,0,NULL,'2025-09-28 09:13:11'),('0ce371f4-57d0-4de2-a924-28cb79513a4b','17ce01f7-aa5a-4cc2-b2ef-cd9da662fae4','CTMFULL','Custom Furniture - Full Custom / Sideboard','Full Custom / Sideboard',1,999.00,999.00,0,NULL,'2025-09-28 09:13:11'),('10a1ab54-efc0-4642-8b58-f7c8e9f9b11f','2b5ce2f3-e165-4c3c-a891-8d2934d914c4','T1013','Pixel 5-Drawer Desk - W100cm / Assembly','W100cm / Assembly',1,399.00,399.00,0,NULL,'2025-09-28 09:13:11'),('10d1c50f-c3ae-4624-a537-62c1c912cd58','b9bbb3d0-283c-4c7a-a005-18f569c0cffb','TV1634/3018-AD','Paisley 1.6m Oak TV Console Cabinet - Oak / Assembly','Oak / Assembly',1,269.00,269.00,0,NULL,'2025-09-28 09:13:11'),('110878f3-7c50-4c3b-a975-464755a84494','d2561b42-bdac-470f-b382-31744cd32190','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('127ff8f3-2392-44be-9c33-9b67103ad593','77830204-e854-4ecc-bafb-e5bbb0e5f02a','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('1ae73175-5004-4407-99f2-4913112eac29','77830204-e854-4ecc-bafb-e5bbb0e5f02a','SB1283/3075-AD','Richmond 1.2m Walnut Shoe Cabinet - Walnut / Assembly','Walnut / Assembly',1,299.00,299.00,0,NULL,'2025-09-28 09:13:11'),('1f31d70e-89d6-4e1c-9d10-2cec328bce3a','d48eccb7-3215-419d-bce6-3d2966366ca3','SR4/3075-AD','Munich 1.2m Walnut Highboard Storage Cabinet - Walnut / Assembly','Walnut / Assembly',1,399.00,399.00,0,NULL,'2025-09-28 09:13:11'),('2152dd34-3683-43ba-8549-1d0b09e8de37','662ea6af-dbed-4f92-82b6-cfbd6a9d94e3','SB1048/3075','Vernetta 100cm Walnut Sliding Shoe Bench with Cushion - Walnut / Assembly','Walnut / Assembly',1,299.00,299.00,0,NULL,'2025-09-28 09:13:11'),('233d5435-9ff5-407d-bd6f-6443a746e590','ac0b012d-7b6d-4fe6-a9ee-e4a7d999ec48','SC5','Vegas 1.2m Oak Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('241110d1-8d87-439d-8d53-60abb938c120','94b75872-762a-469a-b8a8-f6d5f213fa39','SC15/WAL','Vegas 90cm Walnut Shoe Cabinet',NULL,1,149.00,149.00,0,NULL,'2025-09-28 09:13:11'),('2a30f5bf-2398-4187-a058-b7a8edd153be','fcfbfa54-f02b-438f-bb72-301da092ca75','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('2dcc8d53-b483-4f9c-8edf-30640c0a57f4','d68e74cc-3046-4b03-b69b-2f4684cd0b37','SC5/WAL','Vegas 1.2m Walnut 4-Door Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('32eca697-1024-47b7-b7a8-f3e7c0634ee0','17ce01f7-aa5a-4cc2-b2ef-cd9da662fae4','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('333ba056-0458-47a4-ba5f-78256550ab51','47333340-305d-49b7-9867-200fa7da2391','SR6/3036WH-AD','Hamburg 1.4m Pine/White Sideboard - Oak White / Assembly','Oak White / Assembly',1,329.00,329.00,0,NULL,'2025-09-28 09:13:11'),('3a7df599-191c-4f27-91f0-00e18116e954','4102f205-59da-40a6-ae86-7b21fd0927b0','SC18/WAL','Texas 1.2m Walnut Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('401c32da-eec8-466e-bc32-8a283e265b8a','36cbda64-c0e1-4e8e-b008-7124cf505bed','SC15','Vegas 90cm Oak Shoe Cabinet',NULL,1,149.00,149.00,0,NULL,'2025-09-28 09:13:11'),('4025aa98-8891-4057-8cb5-3e772e92e4b4','e57c919a-55dd-404f-9146-79a3f9280e1a','SC18/WAL','Texas 1.2m Walnut Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('42dea9e2-5849-4a1d-8708-a638fdea6a5f','3949baec-c26e-496a-ae06-9f8246f8cfbe','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('4408745b-4213-47af-a370-4096f920675e','36cbda64-c0e1-4e8e-b008-7124cf505bed','SC4','Vegas 60cm Oak Shoe Cabinet',NULL,1,119.00,119.00,0,NULL,'2025-09-28 09:13:11'),('46887c1f-77b9-4720-92ed-ddb3ee8fbae7','5c2dcc6c-978e-4405-8cf7-3390d8b2701d','SC18/WAL','Texas 1.2m Walnut Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('46bdb256-a6e1-4924-8882-be2936c7f3f6','55341832-df80-4495-a35d-1133143555a9','SC5/WAL','Vegas 1.2m Walnut 4-Door Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('4d7f0270-cb20-425d-b319-e332a130c868','f2cc3eff-dad9-45e7-9789-69bf695c3fd0','SC5(X2)','Vegas Oak 1.2m Wide 1.62m High Shoe Cabinet',NULL,1,299.00,299.00,0,NULL,'2025-09-28 09:13:11'),('4e5a5fce-c9b4-433f-8caa-65eb2825982a','c8f9e809-312b-462a-a235-1936c6c388c2','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('52800a8a-439f-4272-9ea6-6b1f4bf1b260','3b6a635e-a05d-44b3-a36a-d9483950d465','WD8003/3036-AD','Vela 80cm Modular Wardrobe - Pine / Assembly','Pine / Assembly',1,459.00,459.00,0,NULL,'2025-09-28 09:13:11'),('67a3cb43-31d0-45ec-b0ae-20f89a54c314','5c2dcc6c-978e-4405-8cf7-3390d8b2701d','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('68ca09ed-b927-4a23-a8b6-3d57a5a17344','3108915d-c558-4ec0-bee6-6f35e908a7fd','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',2,30.00,60.00,0,NULL,'2025-09-28 09:13:11'),('68e78b8b-3a35-4687-8b5e-c3fe29b4c43d','ea8013b5-0287-4759-8f74-11368c6bb993','SC4/WAL','Vegas 60cm Walnut 2-Door Shoe Cabinet',NULL,1,119.00,119.00,0,NULL,'2025-09-28 09:13:11'),('6eddb755-d0fb-40b3-902e-9b99dc26d9d8','55341832-df80-4495-a35d-1133143555a9','SC4/WAL','Vegas 60cm Walnut 2-Door Shoe Cabinet',NULL,1,119.00,119.00,0,NULL,'2025-09-28 09:13:11'),('6fbe3495-c1dd-4057-a329-d0d4d13b2c30','3108915d-c558-4ec0-bee6-6f35e908a7fd','SI1295/3036-AD','Manhattan 1.2m Pine Flat Top Sideboard - Pine / Assembly','Pine / Assembly',1,329.00,329.00,0,NULL,'2025-09-28 09:13:11'),('726aba2b-b16e-4903-a7ab-749d429ffc48','d2561b42-bdac-470f-b382-31744cd32190','SI1685/3045-AD','Monaco 1.6m Maple 4-Door Sideboard - Maple / 95cm / Assembly','Maple / 95cm / Assembly',1,359.00,359.00,0,NULL,'2025-09-28 09:13:11'),('744a410d-5444-475f-8e33-dff3be5243a1','07115680-9a77-45b9-a646-2dc99cf202a9','TV24/1.6/3075-AD','Hamburg 1.6m Walnut TV Console Cabinet - Walnut / Assembly','Walnut / Assembly',1,269.00,269.00,0,NULL,'2025-09-28 09:13:11'),('756b39f2-6323-4de3-ac88-bc0ccadac347','fb04e547-73cd-4487-8a19-99bf521450df','SC15(X2)','Vegas Oak 90cm Wide 1.62m High Shoe Cabinet',NULL,1,249.00,249.00,0,NULL,'2025-09-28 09:13:11'),('75e1674c-d6c4-4dbc-8ab1-586d3a3dae98','e051fa09-97aa-4057-9688-237c6bebcfa7','SC15(X2)/WAL','Vegas Walnut 90cm Wide 1.62cm High Shoe Cabinet',NULL,1,249.00,249.00,0,NULL,'2025-09-28 09:13:11'),('772e6b16-d2b5-44ef-bca5-fba1cc451e50','de2e1533-bdda-43bd-9f3b-41677187edf8','CTMCOLOR','Custom Furniture - Custom Color / Sideboard','Custom Color / Sideboard',1,999.00,999.00,0,NULL,'2025-09-28 09:13:11'),('7c9fdf5e-d09e-4476-99a6-e0e39ca0b106','c8f9e809-312b-462a-a235-1936c6c388c2','SR7/3036(Premium)-AD','Hamburg 1.6m Pine Sideboard - Pine Oak / Assembly','Pine Oak / Assembly',1,369.00,369.00,0,NULL,'2025-09-28 09:13:11'),('802e50ad-af0e-4b52-a660-acc7139a51dd','07115680-9a77-45b9-a646-2dc99cf202a9','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('857ae5d0-bd02-4e35-9710-024b0dc381f2','916612fb-39e6-4368-b6c6-9d9e73e05de4','BT4550/3101','Cubo 45cm Ash/White Bedside Table - Ash/White / Assembly','Ash/White / Assembly',1,199.00,199.00,0,NULL,'2025-09-28 09:13:11'),('8dcb83bd-9090-4d08-a302-e61d20f06bfe','60501e6f-7e73-4223-878d-533facb5fae1','SC5/WAL','Vegas 1.2m Walnut 4-Door Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('8f985165-dbe7-4f79-8eea-8b29d402e62c','4102f205-59da-40a6-ae86-7b21fd0927b0','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('8ff749e1-f41b-4852-b9e2-7ad04785e038','ea8013b5-0287-4759-8f74-11368c6bb993','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('92dc330b-aa13-4eaf-818a-894ccb0e13c0','17ce01f7-aa5a-4cc2-b2ef-cd9da662fae4','CTMFULL','Custom Furniture - Full Custom / Sideboard','Full Custom / Sideboard',1,999.00,999.00,0,NULL,'2025-09-28 09:13:11'),('946f4f9f-0ad3-4c74-98f6-3e9d2f0aabd1','a3b1213b-9d1a-493d-8e0f-7bdb941bce07','SC15/WAL','Vegas 90cm Walnut Shoe Cabinet',NULL,1,149.00,149.00,0,NULL,'2025-09-28 09:13:11'),('96f488bd-d6b4-492c-8351-26c4751072d8','994cfae9-d3a2-4d89-8b4a-54fd1afdfc4b','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('9b9fba08-59cc-4db2-b260-dbf7072bd5a3','0619582a-eaa9-4e64-914e-9e85d017928e','SR5/3036WH','Hamburg 1.2m Pine/White Sideboard - Pine White / Assembly','Pine White / Assembly',1,299.00,299.00,0,NULL,'2025-09-28 09:13:11'),('a4e5b397-3282-4b58-b37d-b5e3db1261a1','3e0b30d3-0e58-42b2-853e-aef2ee0c60cf','SC5','Vegas 1.2m Oak Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('b4551b0d-ccca-4a4b-bfca-a277e3626ca3','994cfae9-d3a2-4d89-8b4a-54fd1afdfc4b','SC18/WAL','Texas 1.2m Walnut Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('bac56a6f-a57e-480f-a229-bec3e5ef656b','3949baec-c26e-496a-ae06-9f8246f8cfbe','SC18/OAK','Texas 1.2m Oak Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('c06f4f62-c84d-41c6-895e-65b00f44723b','17ce01f7-aa5a-4cc2-b2ef-cd9da662fae4','CTMFULL','Custom Furniture - Full Custom / Sideboard','Full Custom / Sideboard',1,999.00,999.00,0,NULL,'2025-09-28 09:13:11'),('c5f2e8b0-0396-40a5-958c-48b092804f37','f2cc3eff-dad9-45e7-9789-69bf695c3fd0','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('c5f6cf6a-6ab8-4395-833a-2582beb8e1b6','c981b1e9-04e6-4912-9a9c-0692a169d62e','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('c7c9e91e-3f45-42aa-bb62-55ae2d7d27bc','df1875fb-694c-487c-97d4-b1fccf83914c','SC4/WAL','Vegas 60cm Walnut 2-Door Shoe Cabinet',NULL,1,119.00,119.00,0,NULL,'2025-09-28 09:13:11'),('c9cbf6e3-b214-407a-b8d1-ed6a8698c672','a9175b35-fafa-4844-9b52-a7426e1f81bd','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('cf071f9b-8b64-4393-91e1-6f7ee5f7161e','c981b1e9-04e6-4912-9a9c-0692a169d62e','SB1204/3045-AD','Osaka 1.2m Maple XL Shoe Cabinet - Maple / Assembly','Maple / Assembly',1,699.00,699.00,0,NULL,'2025-09-28 09:13:11'),('d07deb5a-8623-4feb-b5df-39839b9cc8a0','ea8013b5-0287-4759-8f74-11368c6bb993','SB4311/3045WH-AD','Eden 35cm Maple/White Slim Shoe Cabinet - Maple White / Assembly','Maple White / Assembly',1,259.00,259.00,0,NULL,'2025-09-28 09:13:11'),('d0cc0fca-1b6d-477d-8b1b-fa91542f0cde','660e37b3-e4ba-42c4-b29a-21e23eca9279','SC5','Vegas 1.2m Oak Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('dc275767-29f9-4a2d-bde9-e891f6d9feee','f7d8512f-b2bf-434f-b615-74d57fc9724f','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('de2efa3a-f1ac-4e69-9e9c-d2f6db634471','d68e74cc-3046-4b03-b69b-2f4684cd0b37','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('de599e86-dc75-46b3-99db-dc54c143f0b6','fb04e547-73cd-4487-8a19-99bf521450df','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('debe5063-9c6f-481b-bd06-a3ba5cd1e15c','d7ec5eb9-c1a4-4ffb-8268-01fa708c7818','SC18(X2)/WAL','Texas Walnut 1.2m Wide 1.63m High Shoe Cabinet',NULL,1,299.00,299.00,0,NULL,'2025-09-28 09:13:11'),('e1438cb8-f5f6-4674-95c2-cff89589c4c4','a685f8db-592a-44d3-bcc5-7bd366961923','SC5','Vegas 1.2m Oak Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('e21cb6e9-94ea-4302-8938-35567f67d542','2b53f66b-631d-486a-8c7c-e11adab02c8d','SC5','Vegas 1.2m Oak Shoe Cabinet',NULL,2,169.00,338.00,0,NULL,'2025-09-28 09:13:11'),('e371ca5c-4671-4b4d-b3d9-c1da50afb547','3b6a635e-a05d-44b3-a36a-d9483950d465','CU-1','Soft Close Hinge Upgrade - Upgrade / Soft Close','Upgrade / Soft Close',1,30.00,30.00,0,NULL,'2025-09-28 09:13:11'),('e58173b2-ae71-457d-8df5-f121744e9809','849f1e57-8ee1-4f52-92b2-340d51a75ac1','SR7/3045WH(Premium)-AD','Hamburg 1.6m Maple/White Sideboard - Maple White / Assembly','Maple White / Assembly',1,369.00,369.00,0,NULL,'2025-09-28 09:13:11'),('e6ba5b93-ed1d-4ae2-9511-209c4926ad69','3832dc1c-e8bc-41a0-9b21-a8153586a477','SC15/WAL','Vegas 90cm Walnut Shoe Cabinet',NULL,1,149.00,149.00,0,NULL,'2025-09-28 09:13:11'),('e8bc44e4-da6e-4294-9f77-db9dade9252f','f7d8512f-b2bf-434f-b615-74d57fc9724f','SC4/WAL','Vegas 60cm Walnut 2-Door Shoe Cabinet',NULL,1,119.00,119.00,0,NULL,'2025-09-28 09:13:11'),('e9ba6846-80f1-4392-8682-60ed7e2cbd62','899bbe61-a6c2-4e08-8e53-3b049f2e1fc2','SC18/WAL','Texas 1.2m Walnut Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('eaff2bec-57eb-4d95-aed9-2d96febcb1fb','e0b129f6-85b7-4326-afa5-9f8d5ab957c6','SC4/WAL','Vegas 60cm Walnut 2-Door Shoe Cabinet',NULL,1,119.00,119.00,0,NULL,'2025-09-28 09:13:11'),('f0c7105d-97af-47de-80bc-58d36c2c41d5','fcfbfa54-f02b-438f-bb72-301da092ca75','SC18/WAL','Texas 1.2m Walnut Shoe Cabinet',NULL,1,169.00,169.00,0,NULL,'2025-09-28 09:13:11'),('f547acf2-f45f-4b87-8b2c-17b8b2dfb9cb','6f0f9d4a-88c8-4a95-987f-3357c64bc09e','SR5/3075(Premium)','Hamburg 1.2m Walnut Sideboard - Walnut (Premium) / Assembly','Walnut (Premium) / Assembly',1,299.00,299.00,0,NULL,'2025-09-28 09:13:11'),('fa7371a2-6e7f-458e-86b2-38b4078203ae','bd9c1944-5159-4ce9-a54d-6acfef3ac783','SS6020/3075','Oxford 60cm Walnut Bookcase - Walnut / Assembly','Walnut / Assembly',1,299.00,299.00,0,NULL,'2025-09-28 09:13:11');
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
  `order_type` enum('pre_order','asap','adhoc','custom_date') DEFAULT 'pre_order' COMMENT 'Order type selected by HQ from Shopify order remarks',
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
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES ('0619582a-eaa9-4e64-914e-9e85d017928e','12044','6702780645598','12044','d27a94b5-322d-4690-a571-cb69ebd47962','received','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-21',299.00,'SGD','Lazada','152747431556631',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('07115680-9a77-45b9-a646-2dc99cf202a9','12053','6704747348190','12053','88ae0691-7c1f-487c-ba77-71c51c487a9e','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-22',293.02,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('077da055-a11a-4307-8731-7937cb05e47a','12009','6691280617694','12009','5abf63e2-ca60-4846-b961-a41267aa4b8c','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-14',169.00,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('17ce01f7-aa5a-4cc2-b2ef-cd9da662fae4','12049','6702840873182','12049','8db09d37-153d-419d-9057-a8f321a9d655','received','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-21',1881.60,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('2b53f66b-631d-486a-8c7c-e11adab02c8d','12027','6697106669790','12027','9786b85a-d297-407d-a08f-da40ee509ad9','received','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-18',291.55,'SGD','Shopee','250917QY2WNRRN',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('2b5ce2f3-e165-4c3c-a891-8d2934d914c4','12020','6695018725598','12020','3d8e2de2-471a-4e7d-8fa4-26488fe40171','received','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-16',599.00,'SGD','Store, Store-Shaw','Shopify Order - shopify_draft_order',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('3108915d-c558-4ec0-bee6-6f35e908a7fd','12048','6702840807646','12048','63dfc571-af4e-4c1e-8ea7-695a0184c6ec','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-21',653.60,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('36cbda64-c0e1-4e8e-b008-7124cf505bed','12029','6698095083742','12029','94aa9789-c730-46f5-a932-b7765af8c026','received','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-18',247.94,'SGD','Store-Kinex','Shopify Order - shopify_draft_order',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('3832dc1c-e8bc-41a0-9b21-a8153586a477','12034','6699876122846','12034','e9fd2679-ad74-4607-af2a-cd3872dbd3ad','validated','pre_order',NULL,NULL,1,'2025-10-06','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:04:36',0,'2025-09-19',146.02,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:04:36'),('3949baec-c26e-496a-ae06-9f8246f8cfbe','12016','6693011390686','12016','53f063c1-c0e8-4125-875a-0143ed9ffe87','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-15',165.62,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('3b6a635e-a05d-44b3-a36a-d9483950d465','12030','6698122871006','12030','f71e927a-4961-43e4-b384-a6add1df4a67','validated','pre_order',NULL,NULL,1,'2025-10-06','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:04:36',0,'2025-09-18',479.22,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:04:36'),('3e0b30d3-0e58-42b2-853e-aef2ee0c60cf','12035','6699902173406','12035','bbdf35c1-314b-44a9-97ac-fd217d18c48e','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-19',165.62,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('4102f205-59da-40a6-ae86-7b21fd0927b0','12025','6696648311006','12025','742b3d12-9d7f-40ec-9170-8619b3fff980','validated','pre_order',NULL,NULL,1,'2025-10-06','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:04:36',0,'2025-09-17',195.02,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:04:36'),('47333340-305d-49b7-9867-200fa7da2391','12032','6698185851102','12032','777a19fc-0206-4ce3-911f-a87fef6db17e','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-18',329.00,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('55341832-df80-4495-a35d-1133143555a9','12012','6691397271774','12012','4489a962-f08c-4429-a94d-192df3bafb72','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-14',301.84,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('5c2dcc6c-978e-4405-8cf7-3390d8b2701d','12014','6691582869726','12014','6ce81706-b88f-41a1-a502-77972faf5313','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-14',195.02,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('60501e6f-7e73-4223-878d-533facb5fae1','12019','6694919176414','12019','e7d2ff8c-43a2-4b08-96bb-b581a4b15aca','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-16',165.62,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('660e37b3-e4ba-42c4-b29a-21e23eca9279','12006','6690197143774','12006','77560218-a59b-4387-9d2f-47ecc5e25af1','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-13',165.62,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('662ea6af-dbed-4f92-82b6-cfbd6a9d94e3','12040','6702755315934','12040','95242365-46c3-4aa2-96ad-7e52a2866d66','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-21',293.02,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('6f0f9d4a-88c8-4a95-987f-3357c64bc09e','12043','6702773960926','12043','4ac84907-1c2c-4b85-bc8f-e51299da4474','received','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-21',258.07,'SGD','Shopee','2509213HMT1SAX',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('77830204-e854-4ecc-bafb-e5bbb0e5f02a','12023','6696585855198','12023','0da9a3bd-2ee9-4790-94de-adde24ba5ece','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-17',322.42,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('849f1e57-8ee1-4f52-92b2-340d51a75ac1','12052','6704455680222','12052','c3196ff2-fc62-45c4-a20c-83a89c6c9ba0','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-22',361.62,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('899bbe61-a6c2-4e08-8e53-3b049f2e1fc2','12046','6702832517342','12046','ab652eb1-ce11-446c-af07-0b1d8692329a','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-21',165.62,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('916612fb-39e6-4368-b6c6-9d9e73e05de4','12039','6702747910366','12039','95242365-46c3-4aa2-96ad-7e52a2866d66','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-21',224.42,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('94b75872-762a-469a-b8a8-f6d5f213fa39','12013','6691441049822','12013','4e01f27e-a5a4-4b1a-9d5a-80752a31157b','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-14',146.02,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('994cfae9-d3a2-4d89-8b4a-54fd1afdfc4b','12015','6691656204510','12015','d7c8ee77-74d6-4c26-99b6-ec3759510293','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-14',165.62,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('a3b1213b-9d1a-493d-8e0f-7bdb941bce07','12024','6696588574942','12024','57ae5266-ede9-4529-9173-9a8a299614f3','validated','pre_order',NULL,NULL,1,'2025-10-06','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:04:36',0,'2025-09-17',149.00,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:04:36'),('a685f8db-592a-44d3-bcc5-7bd366961923','12050','6702905917662','12050','9674ad6d-6642-49d8-acd0-5f1d1d172507','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-21',169.00,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('a9175b35-fafa-4844-9b52-a7426e1f81bd','12017','6693064802526','12017','a6c1c993-8cce-4d29-a331-9d1057b39686','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-15',279.00,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('ac0b012d-7b6d-4fe6-a9ee-e4a7d999ec48','12011','6691385835742','12011','0702f80a-92f1-4c29-855d-3b7b7d2f64dc','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-14',165.62,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('b9bbb3d0-283c-4c7a-a005-18f569c0cffb','12007','6690229747934','12007','7b6b9101-cc16-4b51-8311-6c7fee547b68','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-13',263.62,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('bd9c1944-5159-4ce9-a54d-6acfef3ac783','12026','6696654242014','12026','b90b20be-ae8b-49ce-bda5-0ceb15b2f778','received','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-17',299.00,'SGD','Lazada','152554043712094',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('c8f9e809-312b-462a-a235-1936c6c388c2','12008','6691270754526','12008','081f485b-3f65-4166-84e4-89c7266ab49b','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-14',391.02,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('c981b1e9-04e6-4912-9a9c-0692a169d62e','12041','6702761869534','12041','aec0ef35-157d-4d5d-9ed0-c47442bfd2dc','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-21',692.55,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('d2561b42-bdac-470f-b382-31744cd32190','12018','6693545181406','12018','581bd086-5518-4e04-bdb2-e6b34c40e8c7','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-15',389.00,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('d48eccb7-3215-419d-bce6-3d2966366ca3','12028','6698045014238','12028','31bc4b6b-7558-41a0-a864-ac7e7b81fa9f','validated','pre_order',NULL,NULL,1,'2025-10-06','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:04:36',0,'2025-09-18',399.00,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:04:36'),('d68e74cc-3046-4b03-b69b-2f4684cd0b37','12047','6702834811102','12047','3f21fd28-8139-4005-9276-24cc13f68ad8','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-21',195.02,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('d7ec5eb9-c1a4-4ffb-8268-01fa708c7818','12038','6701337772254','12038','a02708eb-26ae-466b-bbc0-4b73427dc723','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-20',322.42,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('de2e1533-bdda-43bd-9f3b-41677187edf8','12022','6695092486366','12022','e1c6c40e-d6a1-4bd4-9a45-40ab8cc51ff1','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-16',322.42,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('df1875fb-694c-487c-97d4-b1fccf83914c','12051','6704413442270','12051','559b7ba4-8e94-448e-9f54-bcac878a54f6','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-22',116.62,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('e051fa09-97aa-4057-9688-237c6bebcfa7','12010','6691334848734','12010','3c0f1a17-9de0-4fe0-924d-a590209aafd7','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-14',249.00,'SGD','','Shopify Order - web',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('e0b129f6-85b7-4326-afa5-9f8d5ab957c6','12031','6698155376862','12031','18ef083a-4dce-48f2-9e17-76b167958ae2','received','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-18',116.62,'SGD','Store-Kinex','Shopify Order - shopify_draft_order',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('e57c919a-55dd-404f-9146-79a3f9280e1a','12005','6690151268574','12005','372241f0-9e4d-4c2f-85e6-3885493cfae2','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-13',165.62,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54'),('ea8013b5-0287-4759-8f74-11368c6bb993','12036','6701158432990','12036','2248d969-08aa-48a5-abdb-05e899fc1ce0','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-20',399.84,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('f2cc3eff-dad9-45e7-9789-69bf695c3fd0','12045','6702807351518','12045','829b3792-16bb-4a19-8611-5f96a5d58ab2','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-21',322.42,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('f7d8512f-b2bf-434f-b615-74d57fc9724f','12042','6702768554206','12042','25936975-6862-4e08-9e86-04144a436163','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-21',146.02,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('fb04e547-73cd-4487-8a19-99bf521450df','12054','6704824615134','12054','11b9a391-b826-4f78-acff-7e2728f499ed','validated','pre_order',NULL,NULL,0,NULL,NULL,NULL,0,'2025-09-22',273.42,'SGD','','Shopify Order - pos',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-28 09:13:11'),('fcfbfa54-f02b-438f-bb72-301da092ca75','12021','6695039303902','12021','2c72c515-7c44-47d6-b41f-c5d0f79f0b6b','validated','pre_order',NULL,NULL,1,'2025-10-03','6f7cf37b-35b6-4be9-8fee-8275526701db','2025-09-30 06:01:54',0,'2025-09-16',199.00,'SGD','','Shopify Order - shopify_draft_order',NULL,0,1,'shopify','2025-09-28 09:13:11','2025-09-30 06:01:54');
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
-- Dumping data for table `schedule_orders`
--

LOCK TABLES `schedule_orders` WRITE;
/*!40000 ALTER TABLE `schedule_orders` DISABLE KEYS */;
INSERT INTO `schedule_orders` VALUES ('1a3de0b0-c2da-43f0-b8f5-cde0149c7f06','d9a35112-4a5c-47bb-ba1e-3acd712444e1','94b75872-762a-469a-b8a8-f6d5f213fa39',NULL,7,'329583',1.32676820,103.84962440,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('245737f0-ccae-4fa4-8ef7-6b61d88b575c','21fa0388-66c4-4c0b-b9f5-f4473c5afd82','d48eccb7-3215-419d-bce6-3d2966366ca3',NULL,1,'310038',1.33531280,103.85542040,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:04:36','2025-09-30 06:04:36'),('2905a7e0-9dc7-453a-821e-853d6c63827a','d9a35112-4a5c-47bb-ba1e-3acd712444e1','077da055-a11a-4307-8731-7937cb05e47a',NULL,4,'320076',1.32521900,103.85435590,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('29aa7002-90d8-47ac-85be-d034d31d7a6b','21fa0388-66c4-4c0b-b9f5-f4473c5afd82','3b6a635e-a05d-44b3-a36a-d9483950d465',NULL,2,'311139',1.33632360,103.84390850,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:04:36','2025-09-30 06:04:36'),('2b6ecbc9-f80e-4577-8613-e4fc07c33ec4','d9a35112-4a5c-47bb-ba1e-3acd712444e1','ac0b012d-7b6d-4fe6-a9ee-e4a7d999ec48',NULL,14,'610119',1.33509910,103.72443630,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('328c9429-04aa-49ab-abf6-61dab3045fce','d9a35112-4a5c-47bb-ba1e-3acd712444e1','60501e6f-7e73-4223-878d-533facb5fae1',NULL,15,'649485',1.34972090,103.70306320,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('3584a0b3-36f9-4443-b3ee-95f491df29ff','d9a35112-4a5c-47bb-ba1e-3acd712444e1','de2e1533-bdda-43bd-9f3b-41677187edf8',NULL,10,'520875',1.35267690,103.93193680,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('39bc97c7-6df1-46c0-b0b0-81f50a05df6a','d9a35112-4a5c-47bb-ba1e-3acd712444e1','b9bbb3d0-283c-4c7a-a005-18f569c0cffb',NULL,12,'538421',1.33893740,103.88306790,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('489725f3-d132-4599-b8c7-bf43ff075497','d9a35112-4a5c-47bb-ba1e-3acd712444e1','3949baec-c26e-496a-ae06-9f8246f8cfbe',NULL,2,'310152',1.33410780,103.84585510,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('4c8d2d06-5646-444f-bf66-636343856869','d9a35112-4a5c-47bb-ba1e-3acd712444e1','c8f9e809-312b-462a-a235-1936c6c388c2',NULL,17,'681688',1.40385860,103.75060840,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('56319dea-901f-4cbd-9e04-e2c7d484306a','d9a35112-4a5c-47bb-ba1e-3acd712444e1','55341832-df80-4495-a35d-1133143555a9',NULL,13,'590011',1.33779790,103.77276090,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('6246b0b0-9abf-4144-8cac-eeea05891a89','d9a35112-4a5c-47bb-ba1e-3acd712444e1','e57c919a-55dd-404f-9146-79a3f9280e1a',NULL,6,'328689',1.32637950,103.86214330,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('8f3b677f-57fb-499d-ab6a-810c468d72bf','21fa0388-66c4-4c0b-b9f5-f4473c5afd82','3832dc1c-e8bc-41a0-9b21-a8153586a477',NULL,4,'460015',1.32086470,103.93556220,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:04:36','2025-09-30 06:04:36'),('97d82fb5-129d-469c-a13c-4ebe74a62540','d9a35112-4a5c-47bb-ba1e-3acd712444e1','5c2dcc6c-978e-4405-8cf7-3390d8b2701d',NULL,3,'311141',1.33565240,103.84588090,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('9c89b61d-c561-4c5b-b92d-47c0f7056794','d9a35112-4a5c-47bb-ba1e-3acd712444e1','e051fa09-97aa-4057-9688-237c6bebcfa7',NULL,16,'650121',1.35151620,103.74788880,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('ae439622-b8b7-4b2e-b02d-fea0fe624af5','21fa0388-66c4-4c0b-b9f5-f4473c5afd82','4102f205-59da-40a6-ae86-7b21fd0927b0',NULL,3,'439271',1.30908490,103.89603510,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:04:36','2025-09-30 06:04:36'),('b1cbc1de-3967-4d2d-81ff-5e3027201bce','d9a35112-4a5c-47bb-ba1e-3acd712444e1','660e37b3-e4ba-42c4-b29a-21e23eca9279',NULL,8,'439423',1.31221690,103.89511590,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('c04af1bc-aac7-440a-bb85-b07f884f8681','21fa0388-66c4-4c0b-b9f5-f4473c5afd82','a3b1213b-9d1a-493d-8e0f-7bdb941bce07',NULL,5,'468790',1.32153850,103.95221070,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:04:36','2025-09-30 06:04:36'),('ce86839f-4a86-4175-8fa4-97db71de3963','d9a35112-4a5c-47bb-ba1e-3acd712444e1','a9175b35-fafa-4844-9b52-a7426e1f81bd',NULL,9,'509051',1.37811460,103.95807490,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('da64c329-3df9-4566-890f-50b2f3f9a6b9','d9a35112-4a5c-47bb-ba1e-3acd712444e1','77830204-e854-4ecc-bafb-e5bbb0e5f02a',NULL,5,'323101',1.32042160,103.85382080,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('e66236de-2eab-4774-a67d-005e32fc0586','d9a35112-4a5c-47bb-ba1e-3acd712444e1','994cfae9-d3a2-4d89-8b4a-54fd1afdfc4b',NULL,1,'188945',1.29753620,103.85572750,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('ef9e0570-59ee-4ddb-b340-474c2a50bd7f','d9a35112-4a5c-47bb-ba1e-3acd712444e1','fcfbfa54-f02b-438f-bb72-301da092ca75',NULL,18,'730793',1.44258680,103.80259640,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54'),('f3b62ce8-2e9a-451e-9bda-3357d38bfee8','d9a35112-4a5c-47bb-ba1e-3acd712444e1','d2561b42-bdac-470f-b382-31744cd32190',NULL,11,'528494',1.36369380,103.95506860,NULL,NULL,30,NULL,'scheduled',0,NULL,'2025-09-30 06:01:54','2025-09-30 06:01:54');
/*!40000 ALTER TABLE `schedule_orders` ENABLE KEYS */;
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
INSERT INTO `user_sessions` VALUES ('0686c022-a4e5-4171-b4dd-ed41a1e16371','6f7cf37b-35b6-4be9-8fee-8275526701db','pbkdf2:sha256:600000$xGDyZvN7aD0w64sv$81214084ad923aec6aec2239b34ad9e53939601132380cc471d589c7719c42de','2025-10-07 06:19:07','2025-09-30 06:19:06','2025-09-30 06:19:06','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36','172.18.0.9'),('0d8e5dc0-45e7-4f2b-b7fc-844e071985f1','6f7cf37b-35b6-4be9-8fee-8275526701db','pbkdf2:sha256:600000$wwMyV2UEZt6iHi2G$b25aebb9d5afe71190a118972744c35aa64942c5cc418d8a239508d06bbe29f4','2025-10-07 05:56:52','2025-09-30 05:56:52','2025-09-30 05:56:52','Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36','172.18.0.9'),('1772dfb4-a7e6-42d7-b625-133b155438be','6f7cf37b-35b6-4be9-8fee-8275526701db','pbkdf2:sha256:600000$luN7jqKTs5G1MK7d$e0636cb9a535c9842db4664378059b3acfcb134b5359dbf2174f989944d70e23','2025-10-07 05:56:52','2025-09-30 05:56:51','2025-09-30 05:56:51','Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36','172.18.0.9'),('3589586e-3dd1-4334-b111-e214e9a20cf6','c1ad6b47-7cd5-402e-b26f-9ccf88c50fc0','pbkdf2:sha256:600000$F2DbisUk8ZJrXRKR$3e292a7de4497b762c738537afc9bc7777dfbdda5cab0d0a5503bef3c5bdc96c','2025-09-27 22:12:33','2025-09-20 22:12:33','2025-09-20 22:12:33','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36','172.18.0.1'),('3d152a80-fe14-4e32-a7e7-43c5640f1ab1','6f7cf37b-35b6-4be9-8fee-8275526701db','pbkdf2:sha256:600000$9nUhOUimKB4uM6wy$c76cbbd73e362a5865c6a22f8db3a87b418aa480eca83534cbef4da0b655c309','2025-10-07 05:56:52','2025-09-30 05:56:51','2025-09-30 05:56:51','Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36','172.18.0.9'),('4f0d7a2b-5d02-49b7-9b21-7847b96fbb1f','6f7cf37b-35b6-4be9-8fee-8275526701db','pbkdf2:sha256:600000$UiCj2eXm1FTAfzyt$ba7f725e5d46209c3db673f3702af52b398b9d167ebf12984ca472dc456297ac','2025-10-07 05:57:29','2025-09-30 05:57:29','2025-09-30 05:57:29','Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36','172.18.0.9'),('8e90f9f7-fe75-4f4e-ab68-94536e67acd0','c1ad6b47-7cd5-402e-b26f-9ccf88c50fc0','pbkdf2:sha256:600000$r1VvYqF3XqEe4ESV$8a9b968c247603239e1774d3701e63add8ba3076695799e7146b4c0d77a3df37','2025-09-27 17:32:06','2025-09-20 17:32:06','2025-09-20 17:32:06','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36','172.18.0.1'),('8f0abe93-720b-40b2-a486-0e8933e02463','c1ad6b47-7cd5-402e-b26f-9ccf88c50fc0','pbkdf2:sha256:600000$ue0QbRLtz1u2evko$f5b71b8ac642f6a657e445fd77323f71989f2e61632f619fd3e0da4ddf2e9c02','2025-10-07 05:49:24','2025-09-30 05:49:24','2025-09-30 05:49:24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36','172.18.0.1'),('ac6d4d75-f0df-493b-ae6e-28824f55efde','c1ad6b47-7cd5-402e-b26f-9ccf88c50fc0','pbkdf2:sha256:600000$eQBvSJqZit7jwzzE$472a86c8caf7865899e3a0a317d8a38d340a345694c373764c927ed519b97a79','2025-09-27 18:51:54','2025-09-20 18:51:53','2025-09-20 18:51:53','Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36','172.18.0.1'),('c44cb116-f218-4163-ae38-c2ba2242bb60','6f7cf37b-35b6-4be9-8fee-8275526701db','pbkdf2:sha256:600000$NQ1ikF4LVJgZ18B1$196ce035a2504db38860e047908bc64ef1f51fcbb1bf6bd4980d01c73cb1698a','2025-10-07 06:19:07','2025-09-30 06:19:06','2025-09-30 06:19:06','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36','172.18.0.9');
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
INSERT INTO `users` VALUES ('4b650253-96c9-11f0-86bc-d2f552c411bd','admin@levels.sg','$2b$12$example_hash_admin','admin',1,NULL,0,NULL,'2025-09-20 16:59:34','2025-09-20 16:59:34'),('4b65046f-96c9-11f0-86bc-d2f552c411bd','warehouse@levels.sg','$2b$12$example_hash_warehouse','warehouse',1,NULL,0,NULL,'2025-09-20 16:59:34','2025-09-20 16:59:34'),('4b650563-96c9-11f0-86bc-d2f552c411bd','driver1@levels.sg','$2b$12$example_hash_driver1','driver',1,NULL,0,NULL,'2025-09-20 16:59:34','2025-09-20 16:59:34'),('4b6505b2-96c9-11f0-86bc-d2f552c411bd','hq@levels.sg','$2b$12$example_hash_hq','hq',1,NULL,0,NULL,'2025-09-20 16:59:34','2025-09-20 16:59:34'),('4b6505f3-96c9-11f0-86bc-d2f552c411bd','cs@levels.sg','$2b$12$example_hash_cs','customer_service',1,NULL,0,NULL,'2025-09-20 16:59:34','2025-09-20 16:59:34'),('6f7cf37b-35b6-4be9-8fee-8275526701db','mervin@levels.sg','pbkdf2:sha256:600000$cPBN3j8Y3pvV8FEr$4b8b2dcb48075f62809922fcb0c38bfe6c5520697ffe99c24d95aa7cebcf7303','admin',1,'2025-09-30 06:19:06',0,NULL,'2025-09-30 05:53:51','2025-09-30 06:19:06'),('c1ad6b47-7cd5-402e-b26f-9ccf88c50fc0','test@levels.sg','pbkdf2:sha256:600000$MV0uvzrKsPaS8neV$bc7e332d77e336977aae1e6ba503f0ef63d15538e57c5844660e847b73ed2967','admin',1,'2025-09-30 05:49:24',0,NULL,'2025-09-20 17:32:04','2025-09-30 05:49:24');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

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
/*!50001 VIEW `v_unscheduled_orders` AS select `o`.`order_id` AS `order_id`,`o`.`order_no` AS `order_no`,`o`.`shopify_order_id` AS `shopify_order_id`,`o`.`order_type` AS `order_type`,`o`.`preferred_delivery_date` AS `preferred_delivery_date`,`o`.`preferred_delivery_time` AS `preferred_delivery_time`,`o`.`status` AS `order_status`,`o`.`order_date` AS `order_date`,`o`.`order_value` AS `order_value`,`o`.`note` AS `order_remarks`,`c`.`customer_id` AS `customer_id`,`c`.`customer_name` AS `customer_name`,`c`.`customer_contact` AS `customer_contact`,`c`.`customer_postal_code` AS `customer_postal_code`,`c`.`customer_street` AS `customer_street`,`c`.`customer_unit` AS `customer_unit`,`c`.`housing_type` AS `housing_type`,`c`.`latitude` AS `latitude`,`c`.`longitude` AS `longitude`,count(`oi`.`item_id`) AS `total_items`,sum((case when (`i`.`assembly_required` = 1) then 1 else 0 end)) AS `items_requiring_assembly`,`o`.`created_at` AS `created_at`,`o`.`updated_at` AS `updated_at` from (((`orders` `o` join `customers` `c` on((`o`.`customer_id` = `c`.`customer_id`))) left join `order_items` `oi` on((`o`.`order_id` = `oi`.`order_id`))) left join `inventory` `i` on((`oi`.`sku` = `i`.`sku`))) where ((`o`.`is_scheduled` = 0) and (`o`.`delivery_completed` = 0) and (`o`.`status` in ('validated','processing','ready_for_delivery'))) group by `o`.`order_id`,`o`.`order_no`,`o`.`shopify_order_id`,`o`.`order_type`,`o`.`preferred_delivery_date`,`o`.`preferred_delivery_time`,`o`.`status`,`o`.`order_date`,`o`.`order_value`,`o`.`note`,`c`.`customer_id`,`c`.`customer_name`,`c`.`customer_contact`,`c`.`customer_postal_code`,`c`.`customer_street`,`c`.`customer_unit`,`c`.`housing_type`,`c`.`latitude`,`c`.`longitude`,`o`.`created_at`,`o`.`updated_at` order by (case `o`.`order_type` when 'asap' then 1 when 'adhoc' then 2 when 'pre_order' then 3 when 'custom_date' then 4 else 5 end),`o`.`order_date` */;
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

-- Dump completed on 2025-10-02 19:16:42
