CREATE TABLE ClientCallRecording(
	Id int  PRIMARY KEY IDENTITY(1,1) NOT NULL,
	ClientId varchar(50) FOREIGN KEY REFERENCES Client(ClientId) NOT NULL,	
	CallFileName varchar(50) NOT NULL,
	CallFilePath varchar(50) NOT NULL,
	UploadDate datetime DEFAULT (GETDATE()) NOT NULL,
	Created datetime DEFAULT (GETDATE()) NOT NULL,
	Modified datetime DEFAULT (GETDATE()) NOT NULL,
	IsActive bit DEFAULT 1,
	IsDeleted bit DEFAULT 0
	)