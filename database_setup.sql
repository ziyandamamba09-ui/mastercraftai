-- Run this SQL in Railway MySQL to set up the database
-- Copy ALL of this and paste into Railway's MySQL query tool

CREATE TABLE IF NOT EXISTS inventory (
  id INT AUTO_INCREMENT PRIMARY KEY,
  item VARCHAR(100),
  quantity INT,
  unit_price DECIMAL(10,2),
  department VARCHAR(50),
  supplier VARCHAR(100),
  reorder_level INT DEFAULT 10,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sales (
  id INT AUTO_INCREMENT PRIMARY KEY,
  month VARCHAR(50),
  amount DECIMAL(10,2),
  invoices INT,
  customer VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS staff (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  department VARCHAR(50),
  role VARCHAR(100),
  salary DECIMAL(10,2),
  start_date DATE
);

CREATE TABLE IF NOT EXISTS expenses (
  id INT AUTO_INCREMENT PRIMARY KEY,
  category VARCHAR(100),
  amount DECIMAL(10,2),
  month VARCHAR(50),
  approved_by VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS attendance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  staff_name VARCHAR(100),
  department VARCHAR(50),
  date DATE,
  time_in TIME,
  time_out TIME,
  status VARCHAR(20) DEFAULT 'Present',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  type VARCHAR(50),
  message TEXT,
  severity VARCHAR(20) DEFAULT 'info',
  is_read TINYINT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS purchase_orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  po_number VARCHAR(20),
  supplier VARCHAR(100),
  item VARCHAR(100),
  quantity INT,
  unit_price DECIMAL(10,2),
  total_amount DECIMAL(10,2),
  department VARCHAR(50),
  status VARCHAR(20) DEFAULT 'Pending',
  requested_by VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS invoices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  invoice_number VARCHAR(20),
  customer_name VARCHAR(100),
  customer_email VARCHAR(100),
  items TEXT,
  subtotal DECIMAL(10,2),
  tax DECIMAL(10,2),
  total DECIMAL(10,2),
  status VARCHAR(20) DEFAULT 'Unpaid',
  due_date DATE,
  created_by VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stock_movements (
  id INT AUTO_INCREMENT PRIMARY KEY,
  item VARCHAR(100),
  movement_type VARCHAR(20),
  quantity INT,
  previous_qty INT,
  new_qty INT,
  reason VARCHAR(200),
  department VARCHAR(50),
  recorded_by VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SAMPLE DATA
INSERT INTO inventory VALUES
(1,'Office Chair',15,1200.00,'Logistics','Furniture World',10,NOW()),
(2,'Laptop Dell',8,12500.00,'IT','Dell Eswatini',5,NOW()),
(3,'A4 Paper Ream',200,65.00,'Admin','Officeworks',20,NOW()),
(4,'Printer Ink Cartridge',30,350.00,'Admin','HP Supplies',10,NOW()),
(5,'Network Switch',4,3200.00,'IT','Cisco Partners',5,NOW());

INSERT INTO sales VALUES
(1,'January 2026',245000.00,42,'Various Clients'),
(2,'February 2026',312000.00,56,'Various Clients'),
(3,'March 2026',289000.00,49,'Various Clients'),
(4,'April 2026',178000.00,31,'Various Clients');

INSERT INTO staff VALUES
(1,'Sipho Dlamini','Accounting','Senior Accountant',18000.00,'2020-03-01'),
(2,'Nomsa Nkosi','IT','Systems Administrator',22000.00,'2019-06-15'),
(3,'Themba Zwane','Sales','Sales Manager',25000.00,'2018-01-10'),
(4,'Bongani Mhlanga','Logistics','Warehouse Supervisor',16000.00,'2021-07-01'),
(5,'Lindiwe Fakudze','Management','Operations Director',35000.00,'2017-04-01');

INSERT INTO expenses VALUES
(1,'Salaries',180000.00,'April 2026','Lindiwe Fakudze'),
(2,'Utilities',12000.00,'April 2026','Lindiwe Fakudze'),
(3,'Rent',25000.00,'April 2026','Lindiwe Fakudze'),
(4,'IT Maintenance',8500.00,'April 2026','Nomsa Nkosi'),
(5,'Transport',6200.00,'April 2026','Bongani Mhlanga');

INSERT INTO purchase_orders VALUES
(1,'PO-2026-001','Dell Eswatini','Laptop Dell',3,12500.00,37500.00,'IT','Approved','Nomsa Nkosi',NOW()),
(2,'PO-2026-002','Furniture World','Office Chair',5,1200.00,6000.00,'Logistics','Pending','Bongani Mhlanga',NOW()),
(3,'PO-2026-003','Officeworks','A4 Paper Ream',100,65.00,6500.00,'Admin','Delivered','Sipho Dlamini',NOW());

INSERT INTO invoices VALUES
(1,'INV-2026-001','Swazi Plaza Ltd','accounts@swaziplaza.co.sz','Consulting Services x5',25000.00,3750.00,28750.00,'Paid','2026-02-28','Themba Zwane',NOW()),
(2,'INV-2026-002','Mountain Inn Hotel','finance@mountaininn.sz','IT Support Services x10',45000.00,6750.00,51750.00,'Unpaid','2026-04-30','Themba Zwane',NOW()),
(3,'INV-2026-003','Government of Eswatini','procurement@gov.sz','Software License x2',80000.00,12000.00,92000.00,'Pending','2026-05-15','Lindiwe Fakudze',NOW());

INSERT INTO notifications VALUES
(1,'SYSTEM','MastercraftAI is now live online. Welcome to the system.','success',0,NOW()),
(2,'LOW_STOCK','Network Switch has only 4 units remaining. Reorder required.','danger',0,NOW());
