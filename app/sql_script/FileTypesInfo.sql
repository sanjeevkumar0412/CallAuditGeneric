CREATE TABLE FileTypesInfo(
	Id int IDENTITY(1,1) NOT NULL,
	ClientId varchar(50) FOREIGN KEY REFERENCES Client(ClientId) NOT NULL,	
	FileType varchar(50) NOT NULL,
	FilePath varchar(max) NOT NULL,
	FileDescription varchar(50),
	Created datetime DEFAULT (GETDATE()) NOT NULL,
	Modified datetime DEFAULT (GETDATE()) NOT NULL,
	IsActive bit DEFAULT 1,
	IsDeleted bit DEFAULT 0
	)