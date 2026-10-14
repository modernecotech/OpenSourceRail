// UI language never changes identifiers, engineering units, permissions or scope.
export const AR={
  Plan:'التخطيط',Design:'التصميم',Deliver:'التنفيذ',Operate:'التشغيل',Maintain:'الصيانة',Assure:'التحقق',
  'task area':'مجال العمل',city:'المدينة',actor:'اسم العرض',role:'دور العرض',mode:'الوضع',language:'اللغة',
  designer:'مصمم',dispatcher:'مراقب حركة',maintainer:'مسؤول صيانة',reviewer:'مراجع',
  design:'تصميم',simulation:'محاكاة',training:'تدريب',live:'تشغيل فعلي',
  overview:'نظرة عامة',verification:'التحقق وبوابات القبول','engineering-change':'التغييرات الهندسية',
  'decision-readiness':'جاهزية القرار','design-options':'خيارات التصميم',studio:'استوديو المدينة',simulator:'المحاكاة',
  'service-planning':'تخطيط الخدمة والعمل الميداني',occ:'مركز التحكم',operations:'أعمال السكك',lifecycle:'الأصول المرتبطة',
  operating:'تنفيذ المدينة',erp:'مساحة الأعمال',projects:'المشاريع والأتمتة',tasks:'المهام',procurement:'المشتريات',
  receipts:'استلام المواد',manufacturing:'التصنيع',quality:'فحوص الجودة',stock:'المخزون',maintenance:'الصيانة',
  issues:'حالات الصيانة',finance:'المالية',people:'الأفراد',fuxa:'المراقبة',
  'auto-design':'التصميم الآلي','design-jobs':'مهام التصميم والنتائج','part-inspector':'فحص الأجزاء والأصول','evidence-intake':'الأفراد ومراجعة الأدلة',
  'Define and run':'التعريف والتنفيذ','Jobs and comparisons':'المهام والمقارنات','Part inspector':'فحص الأجزاء',
  'People and evidence':'الأفراد والأدلة','Run on this machine':'التنفيذ على هذا الجهاز','Refresh jobs':'تحديث المهام',
  'Save draft record':'حفظ مسودة السجل','Person name':'اسم الشخص',Organization:'المؤسسة','Appointed role':'الدور المعيّن',
  'Project, responsibility and limits':'المشروع والمسؤوليات والحدود','Appointment valid until':'سريان التعيين حتى',
  'Record type':'نوع السجل','Retained evidence file':'ملف الأدلة المحفوظ',
  draft:'مسودة',running:'جارٍ التنفيذ','numerically-verified':'متحقق عددياً','physically-correlated':'مطابقة مادية',
  'independently-accepted':'قبول مستقل',passed:'اجتاز',failed:'فشل',stale:'قديمة',unknown:'غير معروف','not-run':'لم ينفّذ',
  'outside-domain':'خارج مجال النموذج',unavailable:'غير متاح','budget-exceeded':'تجاوز الميزانية',cancelled:'ملغى',
};
export function language(){let value=typeof location==='undefined'?null:new URLSearchParams(location.search).get('lang');try{value=value||(typeof localStorage==='undefined'?null:localStorage.getItem('osr:ui:language'));}catch{}return value==='ar'?'ar':'en';}
export function translate(key,fallback=key){return language()==='ar'?(AR[key]||fallback):fallback;}
export function applyLanguage(){document.documentElement.lang=language();document.documentElement.dir=language()==='ar'?'rtl':'ltr';}
