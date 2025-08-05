import random
import time
import logging
import re
import os
import json
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

allowed_users = [5267452039, 6744413466, 6232326259, 7180962743]

words = [
    "قلم", "كتاب", "باب", "شباك", "تفاح", "مطر", "ورد", "وردة", "جبل", "بيت",
    "شمس", "قمر", "نجم", "بحر", "سماء", "سيارة", "قط", "هاتف", "مدرسة", "كرسي",
    "طاولة", "ساعة", "نافذة", "مدينة", "طريق", "حديقة", "شجرة", "حاسوب", "ورقة",
    "قلم رصاص", "شاطئ", "صديق", "قميص", "زهرة", "عين", "نهر", "غابة", "برج",
    "حدود", "مفتاح", "حذاء", "سفينة", "نجمة", "لعبة", "ثوب", "قارب", "مطبخ",
    "شارع", "جدار", "سرير", "مكتبة", "صندوق", "نافورة", "مكتب", "بيتونه", "كهرباء",
    "سكان", "سور", "دانيال", "العظماء", "سكب", "فطور", "دانتي", "سوات", "الملا",
    "اويس", "سسكو", "ميرزا", "دفتر", "سيف", "نار", "كلب", "بنت", "ولد", "نور",
    "ليل", "نهار", "فم", "راس", "انف", "تلفاز", "كنبة", "سطح", "كوخ", "سلة",
    "قوس", "صقر", "ذيب", "نمر", "لبوة", "حوت", "نملة", "ذبابة", "نحلة", "تلفون",
    "قرية", "مطار", "دراجة", "بنطال", "رداء", "جامعة", "لوح", "طباشير", "دواء",
    "صحة", "خبز", "قدر", "ملعقة", "سكين", "كوب", "صحن", "فرن", "سخان", "صابون",
    "مرآة", "مروحة", "بستان", "كرز", "موز", "تمر", "عنب", "ليمون", "برتقال",
    "خوخ", "دبس", "سكر", "ملح", "خل", "زيت", "كعك", "حلوى", "لبن", "جبن", "رز",
    "شاي", "قهوة", "عسل", "قفل", "درج", "جاكيت", "قناع", "حبل", "شبكة", "درع",
    "خوذة", "شنطة", "دلو", "سلم", "طنجرة", "مدفع", "رمح", "درهم", "دينار", "عملة",
    "وقت", "فجر", "ظهر", "عصر", "مغرب", "عشاء", "صوت", "ضوء", "رياح", "سحاب",
    "ثلج", "برد", "حر", "ظل", "نسمه", "هواء", "ارض", "غيم", "مجرة", "كوكب", "شهب",
    "صخرة", "تربة", "تراب", "طين", "رمل", "تل", "وادي", "غزال", "ضبع", "ثعلب",
    "تمساح", "نسر", "بلبل", "حمام", "نعامة", "بط", "وزة", "ديك", "دجاجة", "سمك",
    "قنديل", "سرطان", "سلحفاة", "عصفور", "غراب", "بومة", "دلفين", "دبور", "صرصار",
    "برغوث", "عثة", "دودة", "سوسة", "فأر", "خنزير", "حصان", "بقرة", "جاموس",
    "ماعز", "غنم", "حمار", "جمل", "زرافة", "فهد", "أسد", "تنين", "كنغر", "سنجاب",
    "خلد", "ارنب", "قنفذ", "خفاش", "ببغاء", "نسور", "نورس", "قرش", "اوز", "طاووس",
    "باز", "عقاب", "طائر", "سمكة", "يركض", "يكلل", "يتمرض", "يستشعر", "يتمرن",
    "يتنمر", "يستلذ", "يستغرب", "يستهزئ", "يستوعب", "يتسلق", "ينفعل", "ينكمش",
    "ينفجر", "يتردد", "يتمدد", "يتقلب", "يتغمد", "يبتهج", "يحترق", "يبرد", "يتلطخ",
    "يتقزز", "يتوتر", "يتضخم", "يتأمل", "يتوهج", "يتزود", "يستدرك", "يتصنم",
    "مستلطف", "متهجد", "متوتر", "متغطرس", "متوحد", "متردد", "متلبد", "متكدر",
    "مبهم", "مرتبك", "منزلق", "مربك", "مدمدم", "مشوش", "متعكر", "ممتص", "منكمش",
    "مضطرب", "منهك", "مرهق", "مترمل", "متهكم", "متهور", "متصلب", "مكظوم", "مستتر",
    "مبتهج", "محترز", "مستنزف", "محتدم", "تحكم", "تحمل", "تدحرج", "تجمد", "تشوش",
    "تقهقر", "توجس", "تفرد", "تنكر", "تذبذب", "تكدر", "تلطف", "تململ", "تمدد",
    "تغمد", "تحرر", "تكيف", "تسلل", "تشنج", "تكتم", "توجع", "تحجر", "تهيج", "تجدد",
    "تخدر", "تقلص", "تسكع", "تدافع", "جمود", "حذر", "غموض", "قمع", "قرف", "صمت",
    "كظم", "قنوط", "هلع", "غمغم", "ترقب", "توهج", "وجل", "خجل", "كمون", "كدر",
    "ظلم", "نكد", "غم", "ضيق", "يطفو", "ينحني", "يهمس", "يبكم", "يهجم", "يصمد",
    "يتوه", "يلتف", "بكيم", "اكلال", "حلكة", "دوغم", "يرمش", "يدمدم", "يربت",
    "يتربص", "يهتز", "يسبح", "يتغطى", "يتقلد", "يتلعثم", "يتدفق", "يتشتت",
    "يرتعد", "يتشدد", "ينقض", "ينسدل", "ينهمر", "يتسرب", "يهمد", "يرتقي",
    "ينغمس", "يتفكر", "ينصهر", "يتربد", "يتبعثر"
]
sentences = [
    "السماء صافية اليوم",
    "الورود تنمو في الحديقة",
    "الطيور تغرد فوق الشجر",
    "الشمس تشرق في الصباح",
    "الريح تهب بلطف",
    "الطفل يلعب في الحقل",
    "العصافير تطير في السماء",
    "المدينة جميلة في الليل",
    "الكتب مفيدة للعلم",
    "الصديق يساعد في الشدة",
    "الطريق طويل وواسع",
    "البيت دافئ ومريح",
    "النهر يجري بين الجبال",
    "الحديقة مليئة بالأشجار",
    "القمر يظهر في السماء",
    "الزهور ملونة وجميلة",
    "الطائرة تحلق في الهواء",
    "السيارة تسير بسرعة",
    "العائلة تجمع في العيد",
    "النهار يضيء العالم",
    "الليل هادئ وساحر",
    "الطيور تهاجر في الشتاء",
    "الأطفال يضحكون بفرح",
    "الشجرة كبيرة وقوية",
    "الحياة مليئة بالأمل",
    "الصداقة كنز ثمين",
    "السماء زرقاء وصفية",
    "الريح تحرك الأغصان",
    "الحديقة مكان للراحة",
    "المدينة تعج بالحياة",
    "الكتب نافذة للمعرفة",
    "الطريق يؤدي إلى النجاح",
    "القمر يضيء الليل",
    "الزهور تفوح بالعطر",
    "الطفل يتعلم بسرعة",
    "الطيور تبني أعشاشها",
    "الشمس تغرب في المساء",
    "العصافير تغني بألحان",
    "البيت مليء بالحب",
    "النهر يروي الأرض",
    "الحديقة تزهر في الربيع",
    "السيارة تسير بهدوء",
    "الطائرة تقلع في الصباح",
    "العائلة تجمع حول المائدة",
    "النهار يبدأ بالصلاة",
    "الليل يحمل السكون",
    "الأطفال يلعبون في الحديقة",
    "الشجرة تمنح الظل",
    "الحياة جميلة ومليئة بالفرح",
    "الشياطين هم افضل تيم",
    "دانيال سيعود هنا بعد قليل",
    "تعال نروح نلعب اسرع",
    "علي ولي الله",
]
numbers = [
      # مئات (3 أرقام)
    "189", "012", "013", "031", "098", "091", "567", "898", "132", "101",
    "789", "321", "654", "987", "210", "543", "876", "109", "432", "765",
    "098", "214", "356", "479", "581", "693", "702", "814", "925", "705", "816", "927", "038",
    "149", "260", "371", "482", "593", "604", "715", "826", "937", "048",
    "159", "270", "909", "011", "046", "614", "725", "836", "947", "058",
    "169", "280", "391", "402", "501", "624", "735", "846", "957", "068",

    # مئات آلاف (6 أرقام)
    "651 515", "515 051", "465 103", "654 321", "987 654", "321 987", "065 701", "789 123", "234 567", "041 901",
    "906 606", "073 110", "079 707", "321 654", "965 605", "212 101", "601 101", "019 990",
    "119 901", "158 313", "414 707", "901 101", "603 909", "034 101", "001 101", "665 153","550 616",
    "998 116","002 202", "698 896", "907 709", "076 107", "002 313", "965 143", "515 050",
    "015 951", "613 113", "202 101", "741 901", "798 898", "313 106", "013 313", "087 187", "161 606", "660 116",
    "743 176", "707 701", "007 107", "039 109", "090 109", "109 909", "032 132", "178 781", "576 676", "819 905",
    "961 143", "741 357", "852 951", "963 753", "147 951", "258 753", "369 159", "741 357", "852 951", "045 101",
    "147 258", "258 369", "369 147", "741 963", "852 369", "963 741", "147 852", "258 963", "369 741", "741 369",
    "852 147", "963 258", "147 369", "258 147", "369 258", "741 852", "852 741", "963 147", "159 753", "357 951",

    # ملايين (9 أرقام)
    "991 119 651", "129 651 515", "351 651 515", "123 456 789", "987 654 321", "654 321 987",
    "456 789 123", "321 654 987", "789 123 456", "234 567 890", "567 234 123",
    "890 123 456", "123 890 789", "456 789 321", "789 456 654", "321 654 987",
    "654 321 123", "987 123 456", "123 987 789", "456 321 654", "321 456 987",
    "101 202 303", "202 303 404", "303 404 505", "404 505 606", "505 606 707",
    "606 707 808", "701 312 649", "808 909 101", "909 101 202", "121 212 323",
    "905 506 612", "313 901 156", "914 413 789", "649 531 211", "135 246 357",
    "246 357 468", "357 468 579", "468 579 680", "579 680 791", "901 791 802",
    "791 802 913", "802 913 024", "913 024 135", "024 135 246", "135 246 357",
    "246 357 468", "357 468 579", "468 579 680", "579 680 791", "680 791 802",
    "791 802 913", "802 913 024", "913 024 135", "024 135 246", "135 246 357",
    "246 357 468", "357 468 579", "468 579 680", "579 680 791", "680 791 802",
    "791 802 913", "802 913 024", "913 024 135", "024 135 246", "135 246 357",
    "246 357 468", "357 468 579", "468 579 680", "579 680 791", "680 791 802",
    "791 802 913", "802 913 024", "913 024 135", "024 135 246", "135 246 357",
    "919 961 105", "901 101 056", "901 101 050", "101 098 056", "101 009 090",
    "014 098 056", "701 071 017", "901 019 091", "901 101 026", "501 609 906",
    "550 015 051", "901 101 098", "656 904 004", "101 098 056", "098 098 010", "101 001 010",

    # مليارات (12 رقم)
    "513 456 789 012", "919 651 153 621", "123 456 789 012", "987 654 321 098",
    "654 321 987 654", "456 789 123 456", "321 654 987 321", "789 123 456 789",
    "234 567 890 123", "567 234 123 456", "890 123 456 789", "123 890 789 123",
    "456 789 321 654", "789 456 654 321", "321 654 987 654", "654 321 123 456",
    "987 123 456 789", "123 987 789 123", "456 321 654 987", "321 456 987 654",
    "555 555 555 555", "351 651 515 101", "905 506 612 313", "901 156 914 413",
    "789 649 531 211", "701 312 649 851", "111 222 333 444", "555 666 777 888",
    "999 000 111 222", "333 444 555 666", "777 888 999 000", "123 234 345 456",
    "234 345 456 567", "345 456 567 678", "456 567 678 789", "567 678 789 890",
    "678 789 890 901", "789 890 901 012", "890 901 012 123", "901 012 123 234",
    "012 123 234 345", "123 234 345 456", "234 345 456 567", "345 456 567 678",
    "456 567 678 789", "567 678 789 890", "678 789 890 901", "789 890 901 012",
    "890 901 012 123", "901 012 123 234", "012 123 234 345", "123 234 345 456",
    "234 345 456 567", "345 456 567 678", "456 567 678 789", "567 678 789 890",
    "678 789 890 901", "789 890 901 012", "890 901 012 123", "901 012 123 234",
    "012 123 234 345", "123 234 345 456", "234 345 456 567", "345 456 567 678",
    "901 961 153 621", "101 098 056 021", "112 012 021 001", "653 035 053 001",
    "440 098 015 001", "101 020 002 010", "965 665 489 901", "653 156 489 917",
    "990 019 091 009", "101 098 056 031", "110 010 001 101", "550 015 016 091",
    "995 095 059 010", "404 040 004 405", "313 331 013 107", "565 153 621 909",
    "905 015 056 031", "110 043 079 098", "113 079 048 013", "551 515 101 107",
    "107 007 070 105", "556 361 521 149", "919 642 179 865", "794 781 101 678",

    "981 101 098 053", "913 071 014 101", "113 013 031 202", "101 098 053 661",
    "110 010 020 198", "819 019 091 909", "202 022 020 606", "713 031 013 506",
    "134 976 864 101", "907 743 164 110", "901 101 097 607", "976 656 351 109",
    "991 919 119 698", "101 043 098 202", "789 998 643 521", "156 056 065 103",
    "707 070 007 117", "943 521 115 601", "707 498 676 107", "778 656 313 110",
    "964 178 894 743", "714 587 946 531", "119 091 061 103", "976 167 767 606",
    "956 665 153 507", "616 661 103 106", "061 016 013 101", "905 509 818 108",
    "891 919 607 706", "550 050 056 134", "905 614 212 198", "901 101 097 107",
    "597 879 638 924", "556 665 567 167", "638 843 825 606", "905 541 114 119",
    "656 302 202 104", "404 040 014 141", "606 098 089 515", "501 101 043 187",
    "968 896 698 896", "657 767 798 701", "798 753 651 996", "717 117 468 981"
]

scores = {}
replies = {}
image_replies = {}
pending_replies = {}

def normalize_text(text):
    text = re.sub(r"[^ء-ي0-9]", "", text)
    return text.replace("ه", "ة")

def normalize_number(s):
    return re.sub(r"[^0-9]", "", s)

def clean_user_input(text, bot_username):
    if bot_username and text.endswith(f"@{bot_username}"):
        return text[:-(len(bot_username)+1)].strip()
    return text.strip()

def is_number_answer_correct(user_input, correct_number):
    correct = normalize_number(correct_number)
    user = normalize_number(user_input)
    if user == correct:
        return True
    for digit in correct:
        if digit not in user:
            return False
    user_digits = sorted(set(user))
    correct_digits = sorted(set(correct))
    return user_digits == correct_digits

def is_fakkik_format(user_input, correct_word):
    user_input = normalize_text(user_input.strip())
    correct_word = normalize_text(correct_word.strip())
    pattern = r"^" + r"[\. ]*".join([re.escape(c) for c in correct_word]) + r"[\. ]*$"
    return bool(re.fullmatch(pattern, user_input))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if update.message.chat.type == "private" and user_id not in allowed_users:
        await update.message.reply_text("🚫 هذا البوت خاص.\nراسل المطور لتفعيل الوصول: @h8t99")
        return
    await update.message.reply_text(
        "👋 مرحباً! أرسل:\n"
        "- 'ت' لكلمة مفككة\n"
        "- 'ك' لكلمة بدون تفكيك\n"
        "- 'ر' لرقم\n"
        "- 'ج' لجملة\n"
        "أوامر إضافية:\n"
        "/top - عرض أفضل 5 نقاط\n"
        "اكتب 'تصفير' لتصفير النقاط (للمطور فقط)\n"
        "اكتب 'اضف رد' لإضافة رد تلقائي (نص أو صورة)\n"
        "اكتب 'احذف رد' لحذف رد تلقائي"
    )

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not scores:
        await update.message.reply_text("لا يوجد نقاط حتى الآن.")
        return
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_list = sorted_scores[:5]
    lines = ["🏆 أفضل 5 لاعبين بالنقاط:\n"]
    for rank, (uid, pts) in enumerate(top_list, start=1):
        try:
            member = await context.bot.get_chat_member(update.effective_chat.id, uid)
            username = member.user.username
            display_name = f"@{username}" if username else f"ID: {uid}"
        except:
            display_name = f"ID: {uid}"
        lines.append(f"{rank}. {display_name} — نقاط: {pts}")
    await update.message.reply_text("\n".join(lines))

async def reset_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != 5267452039:
        await update.message.reply_text("🚫 ليس لديك صلاحية تصفير النقاط.")
        return
    scores.clear()
    await update.message.reply_text("✅ تم تصفير جميع النقاط.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message is None:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    chat_type = message.chat.type

    if chat_type == "private" and user_id not in allowed_users:
        user = message.from_user
        username = f"@{user.username}" if user.username else "لا يوجد يوزر"
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        msg = f"📩 شخص حاول استخدام البوت:\n- الاسم: {full_name}\n- اليوزر: {username}\n- الايدي: `{user_id}`"
        await context.bot.send_message(chat_id=5267452039, text=msg, parse_mode="Markdown")
        await message.reply_text("🚫 لا تملك صلاحية استخدام البوت.\nراسل المطور: @h8t99")
        return

    bot_username = (await context.bot.get_me()).username
    text = clean_user_input(message.text or "", bot_username)

    if text == "اضف رد":
        if user_id != 5267452039:
            await message.reply_text("🚫 فقط المطور يمكنه إضافة ردود تلقائية.")
            return
        pending_replies[user_id] = {"step": 1, "mode": "add"}
        await message.reply_text("📌 ارسل الكلمة الي تريد البوت يرد عليها")
        return

    if text == "احذف رد":
        if user_id != 5267452039:
            await message.reply_text("🚫 فقط المطور يمكنه حذف الردود.")
            return
        pending_replies[user_id] = {"step": "delete"}
        await message.reply_text("🗑️ ارسل الكلمة التي تريد حذف الرد الخاص بها")
        return

    if user_id in pending_replies and pending_replies[user_id].get("step") == "delete":
        trigger = text.strip()
        deleted = False
        if trigger in replies:
            del replies[trigger]
            deleted = True
        if trigger in image_replies:
            del image_replies[trigger]
            deleted = True
        del pending_replies[user_id]
        if deleted:
            await message.reply_text(f"✅ تم حذف الرد المرتبط بـ ({trigger})")
        else:
            await message.reply_text(f"❌ لا يوجد رد محفوظ بهذه الكلمة: ({trigger})")
        return

    if user_id in pending_replies:
        step = pending_replies[user_id]["step"]

        if step == 1:
            pending_replies[user_id]["trigger"] = text
            pending_replies[user_id]["step"] = 2
            await message.reply_text("📝 شلون تريده يرد؟ اكتب:\n- `نص` لرد كتابي\n- `صورة` لرد بصورة", parse_mode="Markdown")
            return

        elif step == 2:
            cleaned_text = normalize_text(text.strip().lower())
            if "نص" in cleaned_text:
                pending_replies[user_id]["type"] = "text"
                pending_replies[user_id]["step"] = 3
                await message.reply_text("✍️ اكتب الرد النصي:")
                return
            elif "صورة" in cleaned_text:
                pending_replies[user_id]["type"] = "image"
                pending_replies[user_id]["step"] = 4
                await message.reply_text("🖼️ أرسل الصورة الآن (يمكنك إضافة نص مع الصورة في رسالة واحدة):")
                return
            else:
                if message.photo:
                    pending_replies[user_id]["type"] = "image"
                    file_id = message.photo[-1].file_id
                    trigger = pending_replies[user_id]["trigger"]
                    image_replies[trigger] = file_id
                    caption = message.caption if message.caption else ""
                    if caption.strip():
                        replies[trigger] = caption.strip()
                    del pending_replies[user_id]
                    await message.reply_text(f"✅ تم حفظ الرد بصورة ونص معاً. إذا أحد كتب ({trigger}) البوت يرد بالصورة والنص.")
                    return
                else:
                    await message.reply_text("❌ لازم تكتب: نص أو صورة")
                    return

        elif step == 3:
            trigger = pending_replies[user_id]["trigger"]
            replies[trigger] = text
            del pending_replies[user_id]
            await message.reply_text(f"✅ تم الحفظ. إذا أحد كتب ({trigger}) البوت راح يرد: {text}")
            return

        elif step == 4 and message.photo:
            photo_file = message.photo[-1]
            file_id = photo_file.file_id
            trigger = pending_replies[user_id]["trigger"]
            image_replies[trigger] = file_id
            caption = message.caption if message.caption else ""
            if caption.strip():
                replies[trigger] = caption.strip()
            del pending_replies[user_id]
            await message.reply_text(f"✅ تم حفظ الرد بصورة. إذا أحد كتب ({trigger}) البوت راح يرد بصورة ونص (إذا كان موجود).")
            return

    if text in replies:
        await message.reply_text(replies[text])
        return
    if text in image_replies:
        caption = replies.get(text)
        if caption:
            await message.reply_photo(image_replies[text], caption=caption)
        else:
            await message.reply_photo(image_replies[text])
        return

    if text == "توب":
        await top(update, context)
        return
    if text == "تصفير":
        await reset_top(update, context)
        return

    if text in ["ت", "ك", "ر", "ج"]:
        if text == "ت":
            word = random.choice(words)
            prompt = word
            c_type = "word_fakkik"
        elif text == "ك":
            word = random.choice(words)
            prompt = word
            c_type = "word_plain"
        elif text == "ر":
            number = random.choice(numbers)
            prompt = number
            c_type = "number"
        elif text == "ج":
            sentence = random.choice(sentences)
            prompt = sentence
            c_type = "sentence"
        context.chat_data[chat_id] = {"text": prompt, "type": c_type, "time": time.time(), "winner": None}
        await message.reply_text(prompt)
        return

    challenge = context.chat_data.get(chat_id)
    if challenge and challenge["winner"] is None:
        is_correct = False
        correct = challenge["text"]
        if challenge["type"] == "number":
            is_correct = is_number_answer_correct(text, correct)
        elif challenge["type"] == "word_plain":
            is_correct = normalize_text(text) == normalize_text(correct)
        elif challenge["type"] == "word_fakkik":
            is_correct = is_fakkik_format(text, correct)
        elif challenge["type"] == "sentence":
            is_correct = normalize_text(text) == normalize_text(correct)
        if is_correct:
            challenge["winner"] = user_id
            duration = round(time.time() - challenge["time"], 2)
            scores[user_id] = scores.get(user_id, 0) + 1
            await message.reply_text(f"✅ صحيح!\n🏅 نقاطك: {scores[user_id]}\n⏱️ الزمن: {duration} ثانية")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token("7805017726:AAECaotKq9dsGJUvPaIptzlYCH9k9BvjuDM").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    print("✅ البوت يعمل الآن...")
    app.run_polling()
