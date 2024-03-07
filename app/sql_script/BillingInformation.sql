CREATE TABLE BillingInformation(
	Id int IDENTITY(1,1) NOT NULL,
	BillingId int PRIMARY KEY NOT NULL,
	ClientId varchar(50) FOREIGN KEY REFERENCES Client(ClientId) NOT NULL,	
	SubscriptionId varchar(50) FOREIGN KEY REFERENCES SubscriptionPlan(SubscriptionId) NOT NULL,
	SubscriptionStartDate datetime NOT NULL,
	SubscriptionEndDate datetime NOT NULL,
	PaymentStatus varchar(50) NOT NULL,
	Created datetime DEFAULT (GETDATE()) NOT NULL,
	Modified datetime DEFAULT (GETDATE()) NOT NULL,
	IsActive bit DEFAULT 1,
	IsDeleted bit DEFAULT 0
	)
