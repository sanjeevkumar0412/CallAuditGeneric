CREATE TABLE Client(
	Id int IDENTITY(1,1) NOT NULL,
	ClientId varchar(50) PRIMARY KEY NOT NULL,	
	ClientName varchar(50) NOT NULL,
	ClientEmail varchar(50) NOT NULL,	
	ClientUserName varchar(50) NOT NULL,
	ClientPassword varchar(50) NOT NULL,		
	Created datetime DEFAULT (GETDATE()) NOT NULL,
	Modified datetime DEFAULT (GETDATE()) NOT NULL,
	IsActive bit DEFAULT 0,
	IsDeleted bit DEFAULT 0
	)