#!/usr/bin/env python3
"""
TradeByVee Setup Validator Bot
Forex trade setup scoring system for Telegram
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "8774150209:AAHIxu3j8pEGSB6zODWGF4nEXsJSfZMVj28"

# Validators and Invalidators data
VALIDATORS = {
    'v1': {'name': 'Trend alignment (HTF bias)', 'points': 2},
    'v2': {'name': 'Break of Structure (clean BOS)', 'points': 2},
    'v3': {'name': 'Strong displacement (momentum candle)', 'points': 2},
    'v4': {'name': 'Liquidity sweep (stop hunt)', 'points': 2},
    'v5': {'name': 'Fair Value Gap (FVG)', 'points': 2},
    'v6': {'name': 'Order block reaction', 'points': 1},
    'v7': {'name': 'Supply & demand zone reaction', 'points': 1},
    'v8': {'name': 'Volatility expansion', 'points': 1},
    'v9': {'name': 'Session timing alignment', 'points': 1},
    'v10': {'name': 'Clean RR space', 'points': 2},
}

INVALIDATORS = {
    'i1': {'name': 'Counter-trend entry', 'points': -2},
    'i2': {'name': 'Failure to close after BOS', 'points': -2},
    'i3': {'name': 'Choppy/unclear structure', 'points': -1},
    'i4': {'name': 'Low volatility/no expansion', 'points': -1},
    'i5': {'name': 'Into higher key resistance/support', 'points': -2},
    'i6': {'name': 'Into lower key resistance/support', 'points': -1},
    'i7': {'name': 'Overextended price', 'points': -2},
    'i8': {'name': 'Timeframe conflict', 'points': -2},
    'i9': {'name': 'Weak/indecisive candle closes', 'points': -1},
    'i10': {'name': 'Premature entry (before 70%)', 'points': -1},
    'i11': {'name': 'Long wicks (rejection candles)', 'points': -2},
    'i12': {'name': 'Unmitigated structure', 'points': -2},
}

# User data structure to store selections
user_sessions = {}

def get_user_session(user_id):
    """Get or create user session"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'validators': set(),
            'invalidators': set()
        }
    return user_sessions[user_id]

def calculate_score(session):
    """Calculate score from selected validators and invalidators"""
    validator_score = sum(VALIDATORS[v]['points'] for v in session['validators'])
    invalidator_score = sum(INVALIDATORS[i]['points'] for i in session['invalidators'])
    net_score = validator_score + invalidator_score
    
    return {
        'validators': validator_score,
        'invalidators': invalidator_score,
        'net': net_score
    }

def get_grade_and_verdict(score):
    """Determine grade and verdict from net score"""
    if score >= 8:
        return 'A', '✅ ELITE SETUP - High probability, ideal conditions. Take this trade!'
    elif score >= 4:
        return 'B', '✅ GOOD SETUP - Acceptable confluence. Proceed with confidence.'
    elif score >= 0:
        return 'C', '⚠️ MARGINAL SETUP - Borderline quality. Reduce risk or wait for better.'
    elif score >= -4:
        return 'D', '❌ POOR SETUP - Should avoid. Too many red flags.'
    else:
        return 'F', '🛑 FAILED SETUP - Critical errors. Do NOT trade this!'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    welcome_text = """🎯 *Welcome to TradeByVee Setup Validator!*

Before you enter any trade, validate your setup:
✅ Click the validators present
❌ Click the invalidators present
📊 Get your score + verdict instantly

*No emotions. Just data.*

Type /validate to start scoring your next setup.
Type /help to see all commands.

_From BadLikeVee | Jack of many trades, Midas of all._"""
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """📚 *Available Commands:*

/validate - Start validating a new setup
/score - View current score
/reset - Clear all selections and start fresh
/help - Show this help message

*How it works:*
1. Use /validate to see all validators
2. Click ✅ on factors present in your setup
3. Click ❌ on red flags present
4. Use /score anytime to see your verdict
5. Use /reset to start a new setup

_Happy trading! 📈_"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start validation process - show validators first"""
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    
    keyboard = []
    for key, data in VALIDATORS.items():
        status = '✅' if key in session['validators'] else '☐'
        points_str = f"+{data['points']}"
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {data['name']} ({points_str})",
                callback_data=f"v_{key}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("➡️ Next: Invalidators", callback_data="show_invalidators")])
    keyboard.append([InlineKeyboardButton("📊 View Score", callback_data="show_score")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "🟢 *VALIDATORS (Green Flags)*\n\nClick the validators present in your setup:"
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_invalidators(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show invalidators menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    
    keyboard = []
    for key, data in INVALIDATORS.items():
        status = '❌' if key in session['invalidators'] else '☐'
        points_str = f"{data['points']}"
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {data['name']} ({points_str})",
                callback_data=f"i_{key}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("⬅️ Back: Validators", callback_data="show_validators")])
    keyboard.append([InlineKeyboardButton("📊 View Score", callback_data="show_score")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "🔴 *INVALIDATORS (Red Flags)*\n\nClick the invalidators present in your setup:"
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display current score and verdict"""
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    scores = calculate_score(session)
    grade, verdict = get_grade_and_verdict(scores['net'])
    
    # Build detailed breakdown
    text = f"""📊 *SETUP VALIDATION RESULTS*

*Score Breakdown:*
🟢 Validators: +{scores['validators']}
🔴 Invalidators: {scores['invalidators']}
━━━━━━━━━━━━━━━━
*Net Score: {scores['net']}*
*Grade: {grade}*

*Verdict:*
{verdict}

━━━━━━━━━━━━━━━━
"""
    
    # Add selected validators
    if session['validators']:
        text += "\n✅ *Selected Validators:*\n"
        for v_key in session['validators']:
            text += f"  • {VALIDATORS[v_key]['name']}\n"
    
    # Add selected invalidators
    if session['invalidators']:
        text += "\n❌ *Selected Invalidators:*\n"
        for i_key in session['invalidators']:
            text += f"  • {INVALIDATORS[i_key]['name']}\n"
    
    text += "\n_Use /reset to validate a new setup_"
    
    keyboard = [
        [InlineKeyboardButton("🟢 Back to Validators", callback_data="show_validators")],
        [InlineKeyboardButton("🔴 Back to Invalidators", callback_data="show_invalidators")],
        [InlineKeyboardButton("🔄 Reset All", callback_data="reset_confirm")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset user's selections"""
    user_id = update.effective_user.id
    if user_id in user_sessions:
        user_sessions[user_id] = {'validators': set(), 'invalidators': set()}
    
    await update.message.reply_text(
        "✅ All selections cleared! Use /validate to start a new setup validation.",
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    
    data = query.data
    
    # Navigation buttons
    if data == "show_validators":
        await validate(update, context)
    elif data == "show_invalidators":
        await show_invalidators(update, context)
    elif data == "show_score":
        await show_score(update, context)
    elif data == "reset_confirm":
        session['validators'] = set()
        session['invalidators'] = set()
        await query.edit_message_text(
            "✅ *Reset Complete!*\n\nAll selections cleared. Use /validate to start fresh.",
            parse_mode='Markdown'
        )
    
    # Toggle validators
    elif data.startswith("v_"):
        key = data[2:]
        if key in session['validators']:
            session['validators'].remove(key)
        else:
            session['validators'].add(key)
        await validate(update, context)
    
    # Toggle invalidators
    elif data.startswith("i_"):
        key = data[2:]
        if key in session['invalidators']:
            session['invalidators'].remove(key)
        else:
            session['invalidators'].add(key)
        await show_invalidators(update, context)

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("validate", validate))
    application.add_handler(CommandHandler("score", show_score))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    logger.info("🤖 TradeByVee Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
