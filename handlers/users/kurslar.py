from aiogram import Router,F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile

from keyboards.inline.kurs import *
from keyboards.inline.tolov import tolov_qildim

router = Router()

# 5427009714745517609
@router.callback_query(F.data == "frontend")
async def select_frontend(call: CallbackQuery, state: FSMContext):
    # 1. Foydalanuvchi Frontendni tanlaganini xotiraga yozib qo'yamiz
    await state.update_data(kurs_nomi="Frontend")
    await call.answer()
    photo_url = FSInputFile("handlers/users/img.png")
    new_media = InputMediaPhoto(
        media=photo_url,  # Mahalliy rasm bo'lsa: FSInputFile("rasm_yoli.jpg")
        caption=f"""<tg-emoji emoji-id="5436040291507247633">🎉</tg-emoji><b> Tabriklaymiz</b>
        
<i><b>Siz endilikda Mukamal Frontend darslikni sotib olishingiz mumkun <tg-emoji emoji-id="5431499171045581032">🛒</tg-emoji></b></i>

<b><blockquote expandable>Kursdagi mavzular <tg-emoji emoji-id="5470177992950946662">👇</tg-emoji>

HTML
CSS
Flexbox & Grid
Responsive Design (Media Queries)
Figma (Dizayn bilan ishlash)
SASS / SCSS
Tailwind CSS
Bootstrap
Git & GitHub
JavaScript (ES6+)
DOM API
Asynchronous JavaScript (Promises, Async/Await)
AJAX / Fetch API / Axios
JSON & REST API
Web Storage (LocalStorage, SessionStorage)
NPM / Yarn (Package Managers)
Vite / Webpack (Bundlers)
React.js (yoki Vue.js / Angular)
JSX / TSX
React Hooks (useState, useEffect va boshqalar)
React Router Dom
Redux Toolkit (yoki Zustand / Context API)
TypeScript
Next.js (SSR/SSG uchun)
Vercel / Netlify / GitHub Pages (Deployment)</blockquote></b>

<b>Ushbu <code><blockquote>9860120176007348</blockquote></code> karta raqamga <blockquote><code>74900</code></blockquote> som tolov qiling</b>

Tolov qilib bolgach <b>tolov qildim ✅</b> <i>tugmasini bosing</i>""",
        parse_mode="HTML"
    )
    await call.message.edit_media(
        media=new_media,
        reply_markup=tolov_qildim
    )


@router.callback_query(F.data == "backend")
async def select_backend(call: CallbackQuery, state: FSMContext):
    await state.update_data(kurs_nomi="Backend")

    photo_url = FSInputFile("handlers/users/img_2.png")
    new_media = InputMediaPhoto(
        media=photo_url,
        caption="""<tg-emoji emoji-id="5436040291507247633">🎉</tg-emoji><b> Tabriklaymiz</b>
        
<i><b>Siz endilikda Mukamal Backend darslikni sotib olishingiz mumkun <tg-emoji emoji-id="5431499171045581032">🛒</tg-emoji></b></i>

        
<b>Ushbu <code><blockquote>9860120176007348</blockquote></code> karta raqamga <blockquote><code>54900</code></blockquote> som tolov qiling</b>

Tolov qilib bolgach <b>tolov qildim ✅</b> <i>tugmasini bosing</i>""",
        parse_mode="HTML",
        reply_markup=tolov_qildim
    )
    await call.message.edit_media(
        media=new_media,
        reply_markup=tolov_qildim
    )
    await call.answer()
