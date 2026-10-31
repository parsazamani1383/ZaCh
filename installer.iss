
#define MyAppName "ZaCh"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "ZaCh"
#define MyAppExeName "ZaCh.exe"

[Setup]
AppId={{B73A9C21-6D54-4F82-9B13-8C42A7D1E650}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\ZaCh
DefaultGroupName=ZaCh
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=installer
OutputBaseFilename=ZaCh_Setup
SetupIconFile=assets\images\logo.ico
UninstallDisplayIcon={app}\ZaCh.exe
ArchitecturesInstallIn64BitMode=x64
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "dist\ZaCh\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\ZaCh"; Filename: "{app}\ZaCh.exe"
Name: "{autodesktop}\ZaCh"; Filename: "{app}\ZaCh.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ZaCh.exe"; Description: "Launch ZaCh"; Flags: postinstall nowait skipifsilent


[Code]
var
  GuidePage: TWizardPage;
  GuideMemo: TNewMemo;

procedure InitializeWizard;
begin
  GuidePage := CreateCustomPage(
    wpWelcome,
    'راهنمای استفاده از ZaCh',
    'لطفاً پیش از نصب، این راهنما را مطالعه کنید.'
  );

  GuideMemo := TNewMemo.Create(WizardForm);
  GuideMemo.Parent := GuidePage.Surface;
  GuideMemo.SetBounds(
    0, 0,
    GuidePage.SurfaceWidth,
    GuidePage.SurfaceHeight
  );

  GuideMemo.ReadOnly := True;
  GuideMemo.ScrollBars := ssVertical;
  GuideMemo.WordWrap := True;

  GuideMemo.Lines.Add('راهنمای استفاده از ZaCh');
  GuideMemo.Lines.Add('================================');
  GuideMemo.Lines.Add('');

  GuideMemo.Lines.Add('1. شروع کار');
  GuideMemo.Lines.Add('پس از نصب، برنامه را اجرا کنید و یک گفتگوي جدید ایجاد کنید.');
  GuideMemo.Lines.Add('');

  GuideMemo.Lines.Add('2. فایل های قابل بارگذاری');
  GuideMemo.Lines.Add('شما می توانید فایل های زیر را در برنامه بارگذاری کنید:');
  GuideMemo.Lines.Add('- فایل های متنی (TXT)');
  GuideMemo.Lines.Add('- فایل های Word (DOC و DOCX)');
  GuideMemo.Lines.Add('- فایل های PDF');
  GuideMemo.Lines.Add('- فایل های Excel (XLS و XLSX)');
  GuideMemo.Lines.Add('');

  GuideMemo.Lines.Add('3. چگونه پاسخ های دقیق تری دریافت کنیم؟');
  GuideMemo.Lines.Add('هرچه حجم فایل بارگذاری شده کمتر و محتوای آن متمرکزتر باشد، معمولاً پاسخ های دقیق تر و مرتبط تری دریافت خواهید کرد.');
  GuideMemo.Lines.Add('اگر فایل بزرگی دارید، بهتر است آن را به چند بخش کوچک تر تقسیم کنید.');
  GuideMemo.Lines.Add('سپس هر بخش را در یک گفتگوی جداگانه بارگذاری کنید و سوالات مرتبط با همان بخش را بپرسید.');
  GuideMemo.Lines.Add('به این ترتیب، تمرکز برنامه روی موضوع موردنظر بیشتر خواهد بود.');
  GuideMemo.Lines.Add('');

  GuideMemo.Lines.Add('4. پرسیدن سؤال از اسناد');
  GuideMemo.Lines.Add('پس از بارگذاری و پردازش فایل، سوال خود را در کادر گفتگو بنویسید.');
  GuideMemo.Lines.Add('برای مثال:');
  GuideMemo.Lines.Add('- این فایل را خلاصه کن.');
  GuideMemo.Lines.Add('- نکات مهم این سند چیست؟');
  GuideMemo.Lines.Add('- بخش مربوط به موضوع موردنظر من را توضیح بده.');
  GuideMemo.Lines.Add('');

  GuideMemo.Lines.Add('5. تنظیم کلید API');
  GuideMemo.Lines.Add('برای استفاده از قابلیت های هوش مصنوعی، باید یک کلید API معتبر در تنظیمات برنامه وارد کنید.');
  GuideMemo.Lines.Add('می توانید از ارائه دهندگان سرویس های هوش مصنوعی، از جمله GapGPT، کلید API دریافت کنید.');
  GuideMemo.Lines.Add('برای اطلاعات بیشتر به آدرس زیر مراجعه کنید:');
  GuideMemo.Lines.Add('https://gapgpt.app');
  GuideMemo.Lines.Add('برخی ارائه دهندگان ممکن است پلن رایگان یا اعتبار رایگان ارائه دهند. شرایط و محدودیت ها را در سایت ارائه دهنده بررسی کنید.');
  GuideMemo.Lines.Add('');

  GuideMemo.Lines.Add('6. مدیریت گفتگوها');
  GuideMemo.Lines.Add('از بخش مکالمات می توانید گفتگوهای قبلی خود را مشاهده و ادامه دهید.');
  GuideMemo.Lines.Add('');

  GuideMemo.Lines.Add('نکته امنیتی:');
  GuideMemo.Lines.Add('کلید API شخصی شماست. آن را در اختیار دیگران قرار ندهید.');
end;
