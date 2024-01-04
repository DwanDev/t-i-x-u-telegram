import time
import telebot

# Thay thế bằng token của bot Telegram của bạn
BOT_TOKEN = "6409863109:AAFDtGsMhP-ltFpy-EGSOXq9jymK6zxLy_c"

# Khởi tạo đối tượng TeleBot
bot = telebot.TeleBot(BOT_TOKEN)

# Dictionary để lưu trữ thông tin đặt cược của từng người chơi
betting_info = {}

# Dictionary để lưu thông tin về các bàn cược
table_info = {}

# Biến toàn cục để lưu trữ thông tin người làm nhà cái
bookie_info = {'id': None, 'username': None}

# Biến toàn cục để kiểm tra trạng thái tạo bàn cược
table_creation_in_progress = False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    bot.reply_to(
        message, f"Chào mừng bạn! Id của bạn là: {user_id}\n"
        "Dưới đây là danh sách chức năng:\n"
        "7️⃣ /bet [tài|xỉu] [số_tiền] đặt cược\n"
        "⭕️ /xx tung xúc xắc\n"
        "⭕️ /create_table để tạo bàn cược\n"
        "⭕️ /join_table để tham gia vào bàn cược\n"
        "⭕️ /odds để xem tỷ lệ tài/xỉu\n"
        "⭕️ /start để xem lại danh sách này\n"
        "⭕️ Chú ý: Đây là phiên bản beta, phiên bản hoàn chỉnh sẽ update sau\n"
        "Credit: Dwan https://t.me/DwanDev"
    )

@bot.message_handler(commands=['bet'])
def bet(message):
    global bookie_info, table_creation_in_progress

    # Kiểm tra xem có đang trong quá trình tạo bàn cược không
    if table_creation_in_progress:
        bot.send_message(message.chat.id, "Bàn cược đang được tạo. Vui lòng đợi cho đến khi hoàn thành để đặt cược.")
        return

    # Lấy thông tin đặt cược từ tin nhắn
    try:
        _, bet_type, amount_str = message.text.split(' ', 2)
        amount = int(amount_str)
    except ValueError:
        bot.send_message(message.chat.id, "Cách sử dụng: /bet [tài|xỉu] [số_tiền]")
        return

    user_id = message.from_user.id

    # Kiểm tra xem người chơi đã đặt cược chưa
    if user_id in betting_info:
        bot.send_message(message.chat.id, "Bạn đã đặt cược trước đó. Đợi kết quả trước khi đặt cược lại.")
    else:
        # Lưu thông tin đặt cược của người chơi
        betting_info[user_id] = {'amount': amount, 'bet_type': bet_type}
        bot.send_message(message.chat.id, f"@{bot.get_chat(user_id).username} đã đặt cược {amount}đ cho {bet_type.upper()}.")

@bot.message_handler(commands=['xx'])
def xucxac(message):
    global bookie_info, table_creation_in_progress

    # Kiểm tra xem có nhà cái không
    if bookie_info['id'] is None:
        bot.send_message(message.chat.id, "Chưa có ai làm nhà cái. Ai làm nhà cái sử dụng lệnh /bet để đăng ký.")
        return

    # Kiểm tra xem người gửi có phải là nhà cái không
    if bookie_info['id'] != message.from_user.id:
        bot.send_message(message.chat.id, "Chỉ nhà cái mới có thể sử dụng lệnh /xx.")
        return

    # Sử dụng lệnh send_dice để gửi biểu tượng xúc xắc 3 lần
    results = [bot.send_dice(message.chat.id, emoji='🎲') for _ in range(3)]

    # Tăng thêm thời gian delay
    time.sleep(5)  # Thời gian delay 5 giây

    # Lấy giá trị số từ kết quả xúc xắc
    values = [result.dice.value for result in results]

    # Tính tổng điểm của 3 quả xúc xắc
    total_score = sum(values)

    # Gửi kết quả tổng điểm
    bot.send_message(
        message.chat.id,
        f"🎲 Kết quả xúc xắc: {' '.join(result.dice.emoji for result in results)}\n"
        f"💡 Tổng điểm: {total_score}\n"
        f"🔮 {'Tài' if total_score > 10 else 'Xỉu'}"
    )

    # Tổng hợp thông tin đặt cược
    if betting_info:
        winners = [user_id for user_id, bet_info in betting_info.items() if
                   (bet_info['bet_type'] == 'tài' and total_score > 10) or
                   (bet_info['bet_type'] == 'xỉu' and total_score <= 10)]

        losers = [user_id for user_id in betting_info if user_id not in winners]

        # Gửi thông báo về người thắng và người thua
        if winners:
            msg_winners = "📊 Tổng hợp người thắng cuộc:\nNgười chơi | Loại cược | Số tiền đặt cược | Dự đoán\n---------------------------\n"
            msg_winners += '\n'.join([f"@{bot.get_chat(user_id).username}: {bet_info['bet_type']}  số tiền : {bet_info['amount']} Tài" for user_id, bet_info in betting_info.items() if user_id in winners])
            msg_winners += f"\n---------------------------\nTổng số tiền cược: {sum([bet_info['amount'] for user_id, bet_info in betting_info.items() if user_id in winners])}đ"
            bot.send_message(message.chat.id, msg_winners)

        if losers:
            msg_losers = "📊 Tổng hợp người thua cuộc:\nNgười chơi | Loại cược | Số tiền đặt cược | Dự đoán\n---------------------------\n"
            msg_losers += '\n'.join([f"@{bot.get_chat(user_id).username}: {bet_info['bet_type']}  số tiền : {bet_info['amount']} Xỉu" for user_id, bet_info in betting_info.items() if user_id in losers])
            msg_losers += f"\n---------------------------\nTổng số tiền cược: {sum([bet_info['amount'] for user_id, bet_info in betting_info.items() if user_id in losers])}đ"
            bot.send_message(message.chat.id, msg_losers)

    # Reset thông tin đặt cược và nhà cái
    betting_info.clear()
    bookie_info['id'] = None
    bookie_info['username'] = None

@bot.message_handler(commands=['create_table'])
def create_table(message):
    global bookie_info, table_creation_in_progress

    # Kiểm tra xem có người làm nhà cái không
    if bookie_info['id'] is not None:
        bot.send_message(message.chat.id, "Nhà cái đã được chọn từ trước. Bạn không thể tạo bàn cược mới.")
        return

    # Bắt đầu quá trình tạo bàn cược
    table_creation_in_progress = True

    # Lưu thông tin người tạo bàn cược
    bookie_info['id'] = message.from_user.id
    bookie_info['username'] = bot.get_chat(message.from_user.id).username

    # Thêm thông tin bàn cược vào dictionary
    table_info['table_id'] = {
        'bookie_id': bookie_info['id'],
        'bookie_username': bookie_info['username'],
        'players': [],  # Danh sách người chơi trong bàn
        'betting_info': {},  # Thông tin đặt cược trong bàn
    }

    bot.send_message(message.chat.id, f"Bạn @{bookie_info['username']} đã bắt đầu tạo bàn cược mới. Người chơi có thể tham gia bằng cách sử dụng lệnh /join_table.")

@bot.message_handler(commands=['join_table'])
def join_table(message):
    global table_info, bookie_info, table_creation_in_progress

    # Kiểm tra xem có bàn cược nào đang diễn ra không
    if not table_info or not table_creation_in_progress:
        bot.send_message(message.chat.id, "Hiện tại không có bàn cược nào diễn ra hoặc đang trong quá trình tạo bàn cược.")
        return

    # Lấy thông tin bàn cược hiện tại
    current_table = list(table_info.values())[0]

    # Kiểm tra xem người chơi đã tham gia bàn cược chưa
    if message.from_user.id in current_table['players']:
        bot.send_message(message.chat.id, "Bạn đã tham gia vào bàn cược trước đó.")
        return

    # Thêm người chơi vào danh sách
    current_table['players'].append(message.from_user.id)

    bot.send_message(message.chat.id, f"@{bot.get_chat(message.from_user.id).username} đã tham gia vào bàn cược.")

@bot.message_handler(commands=['odds'])
def view_odds(message):
    global table_info, table_creation_in_progress

    # Kiểm tra xem có bàn cược nào đang diễn ra không
    if not table_info or not table_creation_in_progress:
        bot.send_message(message.chat.id, "Hiện tại không có bàn cược nào diễn ra hoặc đang trong quá trình tạo bàn cược.")
        return

    # Lấy thông tin bàn cược hiện tại
    current_table = list(table_info.values())[0]

    # Tính tỷ lệ dựa trên số lượng người chơi đã đặt cược
    total_bets = sum([bet_info['amount'] for bet_info in current_table['betting_info'].values()])
    odds_tai = 0 if total_bets == 0 else sum([bet_info['amount'] for bet_info in current_table['betting_info'].values() if bet_info['bet_type'] == 'tài']) / total_bets
    odds_xiu = 1 - odds_tai

    bot.send_message(
        message.chat.id,
        f"Tỷ lệ Tài: {odds_tai:.2%}\n"
        f"Tỷ lệ Xỉu: {odds_xiu:.2%}"
    )

@bot.message_handler(commands=['table_info'])
def get_table_info(message):
    global table_info, table_creation_in_progress

    # Kiểm tra xem có bàn cược nào đang diễn ra không
    if not table_info or not table_creation_in_progress:
        bot.send_message(message.chat.id, "Hiện tại không có bàn cược nào diễn ra hoặc đang trong quá trình tạo bàn cược.")
        return

    # Lấy thông tin bàn cược hiện tại
    current_table = list(table_info.values())[0]

    # Lấy số người chơi và thông tin chi tiết
    num_players = len(current_table['players'])
    players_info = "\n".join([f"@{bot.get_chat(user_id).username}" for user_id in current_table['players']])

    # Gửi thông tin về bàn cược
    bot.send_message(
        message.chat.id,
        f"🏓 Bàn cược đang diễn ra:\n"
        f"👤 Số người chơi: {num_players}\n"
        f"👥 Người làm nhà cái: @{current_table['bookie_username']}\n"
        f"👥 Người chơi: {players_info}"
    )

if __name__ == "__main__":
    bot.polling()
