CREATE TABLE Subscriptions(
	Id int IDENTITY(1,1) NOT NULL,
	SubscriptionId varchar(50) PRIMARY KEY NOT NULL,
	ClientId varchar(50) FOREIGN KEY REFERENCES Client(ClientId) NOT NULL,
	SubscriptionPlan  varchar(50) NOT NULL,	
	Created datetime DEFAULT (GETDATE()) NOT NULL,
	Modified datetime DEFAULT (GETDATE()) NOT NULL,
	IsActive bit DEFAULT 1,
	IsDeleted bit DEFAULT 0
	)