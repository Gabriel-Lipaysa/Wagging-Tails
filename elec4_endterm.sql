-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 03, 2026 at 05:47 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `elec4_endterm`
--

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('65937807038e');

-- --------------------------------------------------------

--
-- Table structure for table `carts`
--

CREATE TABLE `carts` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `user_id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `quantity` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `carts`
--

INSERT INTO `carts` (`id`, `user_id`, `product_id`, `quantity`, `created_at`, `updated_at`) VALUES
(8, 8, 6, 1, '2025-12-30 07:32:42', '2025-12-30 07:32:42'),
(9, 8, 5, 12, '2025-12-30 07:32:46', '2025-12-30 07:32:46');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `user_id` bigint(20) UNSIGNED NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `payment_method` enum('gcash','maya','cod','') NOT NULL,
  `status` varchar(255) NOT NULL DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `order_items`
--

CREATE TABLE `order_items` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `order_id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `quantity` int(11) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `price` decimal(8,2) NOT NULL,
  `quantity` int(11) NOT NULL,
  `image` varchar(255) DEFAULT NULL,
  `category` enum('Dog Food','Cat Food') NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`id`, `name`, `description`, `price`, `quantity`, `image`, `category`, `created_at`, `updated_at`) VALUES
(4, 'Pedigree Chicken Canned Dog Food 1.15KG Adult', 'test', 1000.00, 1, 'uploads/375d4c0fa14b4d3bbbab120620af5c94.jpg', 'Dog Food', '2025-11-16 11:03:06', '2025-11-16 11:03:06'),
(5, 'DOG NIGGERRRRRR!!!!!', 'DOGG NIGGER NEW VOLUME', 1000.00, 1, 'uploads/99da8da8dae947e686a5c4272c9b6b1b.png', 'Dog Food', '2025-12-23 16:56:55', '2025-12-23 16:56:55'),
(6, 'Wild Willy Weed (Catnip)', 'Catnip is grown without chemicals on the farm.', 127.00, 3, 'uploads/659721aed4d54802a6d2638047024756.jpg', 'Cat Food', '2025-12-29 17:34:11', '2025-12-29 17:34:11'),
(7, 'Pedigree Adult Beef Chunks in Gravy Wet Dog Food 130g (12 pouches)', 'fods', 124.00, 127, 'uploads/f622155816dc42d8ad193b760d087538.jpg', 'Dog Food', '2025-12-29 17:50:33', '2025-12-29 17:50:33'),
(8, 'Healthy Chunky Beef & Chicken Dog Food - 1/2 Kilo', 'Cooked and ready to serve!\r\n\r\n100% Money back guarantee if your pet doesn’t love our food.\r\nDelivery 1-3 days, but normally it is next day delivery for all orders placed before midnight.\r\n\r\nWhat made BidaBest Pet\'s Chunky Beef & Chicken Dog Food a healthy meal for your dog?\r\n\r\nNo Preservatives\r\nAll Fresh Meat (Beef, Chicken)\r\nAll Fresh Vegetables (Squash, Sweet Potato)\r\nNot processed\r\nMade and served in the Philippines!\r\nCheck out the vitamins and minerals that your dog can gain from this meal below!\r\n\r\nHow long does it last?\r\n\r\nPlease Keep in freezer (up to 3 months) until use.\r\nOnce defrosted, keep refrigerated and use within 3 Days.\r\nHow to prepare the food?\r\n\r\nPreparing our food is very easy! Just follow these steps:\r\n\r\nDefrost at room temperature or over night in the refrigerator\r\nServe pet food at room temperature or chilled.\r\n \r\n\r\n \r\n\r\nBidaBest Chunky Beef & Chicken Dog Food Meets and exceeds AAFCO standards for Growth & Reproduction and Adult Maintenance Using Nutritional Calculations, Lab testing and feeding trials.\r\n\r\nIngredients: Chicken, Beef, Chicken Bone Broth, Squash, Sweet Potato, Beef Hearts, Beef Liver.\r\n\r\nVitamins Added: Taurine, Vit E, Zinc, Manganese, Fish oil, Copper, B1, B2, B3, B5, B6, B9, B12, Biotin, Choline, inositol\r\n\r\nChunky Beef Lab Testing from SGS labs based on 134 Kcal in 100 grams\r\n\r\nMoisture: 74% Crude Protein: 13.69% Crude Fat: 8.56% Crude Fiber: 1.05% Total Carbohydrates: 0.56% Kcal from Carbs: 2.24 Kcal from fat: 77.04 Kcal from protein: 54.75 Total Calories: 134.04 Sodium: 173mg Ash: 2.51% Calcium: 0.387% Phosphorus: 0.253%', 119.00, 5, 'uploads/4174225f7f4446ad96d8277a050214d1.png', 'Dog Food', '2026-01-02 13:11:06', '2026-01-02 13:11:06'),
(9, 'Special Delight Adult Smoked Chicken with Mixed Veggies Wet Dog Food 130g (10 pouches)', 'Formulated with the highest quality ingredients, Special Delight is designed to meet the nutritional needs of all adult dogs. We have carefully selected a blend of essential vitamins and minerals to ensure that every dog receives the best possible nutrition to support their overall health and well-being.\r\nOffers essential vitamins, minerals and high-quality protein, For muscle maintenance and energy, support overall health and well-being.', 350.00, 5, 'uploads/10fafe8b64bc4fba9d4897d9f2bdedcf.png', 'Dog Food', '2026-01-02 13:14:18', '2026-01-02 13:14:18'),
(10, 'Special Delight Puppy Roast Beef Chunk in Gravy Wet Dog Food 130g (10 pouches)', 'Made with premium ingredients specially selected to meet the nutritional needs of growing puppies, Special Delight Puppy is the ultimate choice for nourishing and nurturing your puppies during their crucial early years. It provides essential nutrients for healthy development and optimal growth.\r\nPacked with vital nutrients like Iron, Zinc, and B vitamins,Supports muscle development and overall growth, Important for healthy development of immune function', 350.00, 5, 'uploads/3ab670511bc7417e9c2f14badac62961.png', 'Dog Food', '2026-01-02 13:17:35', '2026-01-02 13:17:35'),
(11, 'Special Delight Adult Salmon Flavor Chunk in Gravy Wet Dog Food 130g (10 pouches)', 'Formulated with the highest quality ingredients, Special Delight is designed to meet the nutritional needs of all adult dogs. We have carefully selected a blend of essential vitamins and minerals to ensure that every dog receives the best possible nutrition to support their overall health and well-being.\r\nRich in omega-3 fatty acids, Packed with Vitamin D and B vitamins, Promote strong bones and healthy immune system.', 350.00, 5, 'uploads/0a6534df64524a4cae3b2848a52aab24.png', 'Dog Food', '2026-01-02 13:18:26', '2026-01-02 13:18:26'),
(12, 'Special Delight Adult Roast Beef Chunk in Gravy Wet Dog Food 130g (10 pouches)', 'Formulated with the highest quality ingredients, Special Delight is designed to meet the nutritional needs of all adult dogs. We have carefully selected a blend of essential vitamins and minerals to ensure that every dog receives the best possible nutrition to support their overall health and well-being.\r\nPacked with vital nutrients like Iron, Zinc, and B vitamins, Support immune function and healthy skin, For overall vitality.', 1000.00, 5, 'uploads/df37b2c051134e65a11f43a84c60c87a.png', 'Dog Food', '2026-01-02 13:19:31', '2026-01-02 13:19:31');

-- --------------------------------------------------------

--
-- Table structure for table `reviews`
--

CREATE TABLE `reviews` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `user_id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `rating` int(11) NOT NULL,
  `comment` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `name` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `phone_number` int(11) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','user') DEFAULT 'user',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `username`, `phone_number`, `address`, `email`, `password`, `role`, `created_at`, `updated_at`) VALUES
(1, 'Admin', 'admin', 0, NULL, 'admin@example.com', 'admin123', 'admin', '2025-10-20 15:24:00', '2025-10-20 15:24:00'),
(3, 'Ines Valeztana', 'ines1999', 0, NULL, 'ines@gmail.com', 'ines123', 'user', '2025-11-16 13:05:33', '2025-11-16 13:05:33'),
(8, 'Carcel Escalante', 'carcel', 0, NULL, 'carcel@gmail.com', 'carcel123', 'user', '2025-11-16 13:15:33', '2025-11-16 13:15:33');

-- --------------------------------------------------------

--
-- Table structure for table `wishlists`
--

CREATE TABLE `wishlists` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `user_id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `wishlists`
--

INSERT INTO `wishlists` (`id`, `user_id`, `product_id`, `created_at`) VALUES
(26, 8, 5, '2026-01-02 05:21:04');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `carts`
--
ALTER TABLE `carts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indexes for table `order_items`
--
ALTER TABLE `order_items`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `order_id` (`order_id`),
  ADD UNIQUE KEY `product_id` (`product_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `reviews`
--
ALTER TABLE `reviews`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `wishlists`
--
ALTER TABLE `wishlists`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`,`product_id`),
  ADD KEY `product_id` (`product_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `carts`
--
ALTER TABLE `carts`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `order_items`
--
ALTER TABLE `order_items`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `reviews`
--
ALTER TABLE `reviews`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `wishlists`
--
ALTER TABLE `wishlists`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `carts`
--
ALTER TABLE `carts`
  ADD CONSTRAINT `carts_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `carts_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `order_items`
--
ALTER TABLE `order_items`
  ADD CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `reviews`
--
ALTER TABLE `reviews`
  ADD CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `wishlists`
--
ALTER TABLE `wishlists`
  ADD CONSTRAINT `wishlists_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `wishlists_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
