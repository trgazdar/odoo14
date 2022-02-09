{
	"name": "台灣會計傳票列印",
	"version": "1.0", 
	"depends": [
		"base",
		"account",
		#"account_invoicing"
	], 
	'summary': '依台灣傳票列印習慣設計傳票列印功能',
	"author": "Smith Lin [yuanchih-consult.com]",
	"website": "www.yuanchih-consult.com",
	"category": "Accounting",
	"description": """
使用說明
======================================================================

- 本模組設計進行列印日記帳分錄(會計傳票)
- 使用方法: 依以下路徑進入：會計>主辦會計>會計分錄>日記帳分錄, 
- 勾選需要列印的項目後，點選列印>記帳憑證
- 列印後將紀錄列印時間以及已列印之紀錄，可於進階篩選中進行已列印以及待列印項目之篩選
- 當日記帳分錄內容有變更時，已列印紀錄將取消勾選
- 可使用分組>前次列印時間進行分組

其他說明
- 預設改以 HTML 直接於頁面上預覽, 確定無誤後可再按[列印], 即可輸出成PDF下載使用

""",
	"data": [
		"report/account_move.xml",
		"views/account_move.xml",
	],
	"installable": True,
	"application": True,
	"auto_install": False,
}