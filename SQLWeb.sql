CREATE DATABASE GreenCorner;
GO
USE GreenCorner;
GO

CREATE TABLE Users (
    UserId INT IDENTITY(1,1) PRIMARY KEY,
    FullName NVARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    Phone VARCHAR(20) NULL,
    Address NVARCHAR(255) NULL,
    Role VARCHAR(20) NOT NULL DEFAULT 'Customer',
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE()
);
GO

CREATE TABLE Categories (
    CategoryId INT IDENTITY(1,1) PRIMARY KEY,
    CategoryName NVARCHAR(100) NOT NULL UNIQUE,
    Description NVARCHAR(255) NULL
);
GO

CREATE TABLE Products (
    ProductId INT IDENTITY(1,1) PRIMARY KEY,
    CategoryId INT NOT NULL,
    ProductName NVARCHAR(150) NOT NULL,
    Price DECIMAL(18,2) NOT NULL,
    Quantity INT NOT NULL DEFAULT 0,
    ImageUrl NVARCHAR(255) NULL,
    Description NVARCHAR(MAX) NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_Products_Categories
        FOREIGN KEY (CategoryId)
        REFERENCES Categories(CategoryId)
);
GO

INSERT INTO Categories (CategoryName, Description)
VALUES
(N'Sen đá', N'Các loại sen đá mini'),
(N'Xương rồng', N'Các loại xương rồng để bàn'),
(N'Cây để bàn', N'Cây cảnh nhỏ dùng trang trí bàn làm việc'),
(N'Cây phong thủy', N'Cây cảnh mang ý nghĩa phong thủy'),
(N'Chậu cây', N'Các loại chậu dành cho cây cảnh mini');

INSERT INTO Products
(
    CategoryId,
    ProductName,
    Price,
    Quantity,
    ImageUrl,
    Description
)
VALUES
(
    1,
    N'Sen đá kim cương',
    79000,
    20,
    N'sen-da-kim-cuong.jpg',
    N'Sen đá mini nhỏ gọn, thích hợp trang trí bàn làm việc.'
),
(
    2,
    N'Xương rồng tai thỏ',
    69000,
    15,
    N'xuong-rong-tai-tho.jpg',
    N'Xương rồng tai thỏ dễ chăm sóc và phù hợp để bàn.'
),
(
    4,
    N'Cây kim tiền mini',
    149000,
    10,
    N'cay-kim-tien.jpg',
    N'Cây kim tiền mini mang ý nghĩa may mắn và tài lộc.'
),
(
    3,
    N'Cây trầu bà để bàn',
    99000,
    12,
    N'cay-trau-ba.jpg',
    N'Cây trầu bà xanh mát, phù hợp trang trí không gian làm việc.'
);
GO

CREATE TABLE Orders (
    OrderId INT IDENTITY(1,1) PRIMARY KEY,
    UserId INT NOT NULL,
    ReceiverName NVARCHAR(100) NOT NULL,
    Phone VARCHAR(20) NOT NULL,
    Address NVARCHAR(255) NOT NULL,
    TotalAmount DECIMAL(18,2) NOT NULL,
    Status NVARCHAR(30) NOT NULL DEFAULT N'Chờ xác nhận',
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_Orders_Users
        FOREIGN KEY (UserId)
        REFERENCES Users(UserId)
);
GO

CREATE TABLE OrderDetails (
    OrderDetailId INT IDENTITY(1,1) PRIMARY KEY,
    OrderId INT NOT NULL,
    ProductId INT NOT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(18,2) NOT NULL,

    CONSTRAINT FK_OrderDetails_Orders
        FOREIGN KEY (OrderId)
        REFERENCES Orders(OrderId),

    CONSTRAINT FK_OrderDetails_Products
        FOREIGN KEY (ProductId)
        REFERENCES Products(ProductId)
);
GO