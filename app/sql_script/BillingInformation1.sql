CREATE TABLE BillingInformation(
	Id int NOT NULL,
	ClientId varchar(50) FOREIGN KEY REFERENCES Client(ClientId) NOT NULL,
	SubscriptionId  int FOREIGN KEY REFERENCES Subscriptions(Id) NOT NULL,
	SubscriptionStartDate datetime NOT NULL,
	SubscriptionEndDate datetime NOT NULL,
	PaymentStatus varchar(50) NOT NULL,
	Created datetime,
	Modified datetime,
	IsActive bit DEFAULT 0,
	IsDeleted bit DEFAULT 0
	)