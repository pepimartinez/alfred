# TODO extensions need names, menus, and commands
# TODO create default menues/commands like starting bot, restart, etc
# TODO utils file to help create menues, etc.
# TODO in core just check config and import all modules and create handlers/pass on api keys

# TODO also need testing/logging/error handleing
# TODO deployment
import logging
import config
import modules
import utils
import importlib
import os
import sys
from threading import Thread
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    CommandHandler,
    Updater,
    CallbackQueryHandler
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


class Alfred(object):
    def __init__(self):
        self.updater = Updater(config.telegram['token'])
        self.dp = self.updater.dispatcher
        self.modules = self.import_active_extensions()
        self.add_default_handlers()
        self.add_module_handlers()

    def import_active_extensions(self):
        extensions = config.extensions
        modules = []
        for dict in extensions:
            if dict['active']:
                module = importlib.import_module('modules.{}.core'.format(dict['name']).lower(), '.')
                modules.append(module.Module())
        return modules

    def add_default_handlers(self):
        self.dp.add_handler(CommandHandler('start', self.start))
        self.dp.add_handler(CallbackQueryHandler(self.main_menu, pattern='main'))
        self.dp.add_handler(CommandHandler('restart', self.restart))
        self.dp.add_error_handler(self.error)

    def add_module_handlers(self):
        for module in self.modules:
            logger.info("Adding module handler: {}".format(module.name))
            self.dp.add_handler(
                CallbackQueryHandler(
                    module.main_menu, pattern='{}-main'.format(module.name)))
            self.dp.add_handler(
                CallbackQueryHandler(
                    module.callback_handler))

    def main_menu(self, bot, update):
        query = update.callback_query
        logger.info("query: {}".format(query))
        bot.edit_message_text(chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="Commands",
            reply_markup=self.main_menu_keyboard())
    
    def main_menu_keyboard(self):
        keyboard = utils.get_extension_keyboards()
        return InlineKeyboardMarkup(keyboard)

    def start(self, bot, update):
        update.message.reply_text("Modules",
            reply_markup=self.main_menu_keyboard())

    def stop_and_restart(self):
        self.updater.stop()
        os.execl(
            sys.executable,
            sys.executable,
            * sys.argv
        )

    def restart(self, bot, update):
        update.message.reply_text('🖥 restarting system...')
        Thread(target=self.stop_and_restart).start()
        update.message.reply_text('🖥 system back online!')

    def error(self, bot, update, error):
        logger.warning(
            'Update "%s" caused error "%s"',
            update,
            error
        )

    def run(self):
        logging.info("Starting bot polling")
        self.updater.start_polling()
        self.updater.idle()


def main():
    al = Alfred()
    al.run()


if __name__ == '__main__':
    main()