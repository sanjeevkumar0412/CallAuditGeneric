CREATE TABLE Logs(
	Id int IDENTITY(1,1) NOT NULL,
	ClientId varchar(50) FOREIGN KEY REFERENCES Client(ClientId) NOT NULL,	
	LogType  varchar(max) NOT NULL,
	LogSummary varchar(max) NOT NULL,
	ModulName varchar(max) NOT NULL,
	LogDetails  varchar(max) NOT NULL,
	Severity varchar(max) NOT NULL,
	LogDate datetime NOT NULL,	
	Created datetime DEFAULT (GETDATE()) NOT NULL,
	Modified datetime DEFAULT (GETDATE()) NOT NULL	
	)