from ttf import Ttf

def main():
	ss()
	# merge()

def ss():
	font = Ttf("JETBRAINSMONO-REGULAR.TTF")
	output = "JETBRAINSMINE.TTF"

	font.restyle("t", "cv02")
	font.restyle("j", "cv04")
	font.restyle("l", "cv05")
	font.restyle("m", "cv06")
	font.restyle("w", "cv07")
	font.restyle("W", "cv07")
	font.restyle("$", "cv14")
	font.restyle("&", "cv15")
	font.restyle("Q", "cv16")
	font.restyle("f", "cv17")
	font.restyle("2", "cv18")
	font.restyle("6", "cv18")
	font.restyle("9", "cv18")

	font.rename("JetBrainsMine", "JetBrainsMine Regular", "JetBrainsMine-Regular")
	font.save_font(output)

def merge():
	font_en = Ttf("JETBRAINSMONO-REGULAR.TTF")
	font_jp = Ttf("ZenMaruGothic-Regular.ttf", 3, 1)
	output = "ZetBrainsMaru.ttf"

	def merge(start, end, label = ""):
		count = 0
		size = end - start
		for cp in range(start, end + 1):
			g = font_jp.get_glyf(cp)
			h = font_jp.get_hmtx(cp)
			if g is None or h is None:
				continue
			font_en.merge(cp, g, h)
			count += 1
			per = (cp - start) * 20 // size
			print(f"\r{label} [{'*' * per}{' ' * (20 - per)}]", end="")
		print(f"\033[32m\n{count}/{size} charactors has marged.\033[0m")

    # default cmap = (3, 10)
	merge(0x3000, 0x30FF, "Kana ")
	merge(0x4E00, 0x9FFF, "Kanji")
	merge(0xFF00, 0xFF9F, "Other")

	font_en.set_cmap(3, 10)
	# 今回のfont_jpはcmap(3, 10)がないのでそのまま
	merge(0x3000, 0x30FF, "Kana ")
	merge(0x4E00, 0x9FFF, "Kanji")
	merge(0xFF00, 0xFF9F, "Other")
	
	font_en.enable_jp() # サクラ上で文字セット：日本語を追加する
	font_en.rename("ZetBrainsMaru", "ZetBrainsMaru Regular", "ZetBrainsMaru-Regular")
	font_en.save_font(output)


if __name__ == '__main__':
	main()
