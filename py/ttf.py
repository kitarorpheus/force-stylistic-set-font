from fontTools.ttLib import TTFont

class Ttf:
	def __init__(self, font, plt=3, enc=10):
		self.font = TTFont(font)
		self.set_cmap(plt, enc)
		self.gsub = self.font["GSUB"].table
		self.build_map()
	
	def set_cmap(self, p, e):
		self.cmap = self.font["cmap"].getcmap(p, e).cmap
	
	def get_support(self):
		for t in self.font["cmap"].tables:
			# 3, 1 はunicode2.0 bmp (format4)
			# 3, 10 はunicode2.0 full (format12)
			print(f"プラットフォームid: {t.platformID}, エンコーディングid: {t.platEncID}, cmapサイズ: {len(t.cmap)}")

	def _get_cmap(self, cp):
		# ない場合はつくる
		if not isinstance(cp, int):
			cp = ord(cp)
		if not cp in self.cmap:
			self.cmap[cp] = f"uni{cp:04X}"
		return self.cmap[cp]
		
	def get_glyf(self, cp):
		if not isinstance(cp, int):
			cp = ord(cp)
		if not cp in self.cmap:
			return None
		tmp = self.font["glyf"][self.cmap[cp]]
		# if tmp.isComposite():
			# err(f"warning: The glyph of Uni({cp}) is cmposite.", file=sys.stderr)
		return tmp
	
	def get_hmtx(self, cp):
		if not isinstance(cp, int):
			cp = ord(cp)
		if not cp in self.cmap:
			return None
		return self.font["hmtx"][self.cmap[cp]]
	
	def merge(self, cp, g, h):
		if not isinstance(cp, int):
			cp = ord(cp)
		c = self._get_cmap(cp)
		self.font["glyf"][c] = g
		self.font["hmtx"][c] = h
	
	def enable_jp(self):
		os2 = self.font["OS/2"]
		os2.ulCodePageRange1 |= (1 << 17)

	def rename(self, family, full, postscript):
		for rec in self.font["name"].names:
			# font family
			if rec.nameID == 1:
				rec.string = family.encode(rec.getEncoding())
			# font display
			if rec.nameID == 4:
				rec.string = full.encode(rec.getEncoding())
			# unique id
			if rec.nameID == 6:
				rec.string = postscript.replace(" ", "").encode(rec.getEncoding())

	def save_font(self, path):
		self.font["maxp"].numGlyphs = len(self.font["glyf"])
		self.font.save(path)

	def build_map(self):
		self.mapping = {}
		for f in self.gsub.FeatureList.FeatureRecord:
			result = {}
			for idx in f.Feature.LookupListIndex:
				for sub in self.gsub.LookupList.Lookup[idx].SubTable:
					if hasattr(sub, "mapping"):
						result.update(sub.mapping)
			if result:
				self.mapping[f.FeatureTag] = result
	
	def list_map(self):
		log("tag: {cmap[codepoint]: cmap[codepoint.alt]}")
		for tag, f in self.mapping.items():
			print(f"{tag}: {f}")
	
	def restyle(self, cp, tag):
		if not isinstance(cp, int):
			cp = ord(cp)
		g = self.cmap[cp]
		alt = self.mapping[tag][g]
		self.font["glyf"][g] = self.font["glyf"][alt]
		self.font["hmtx"][g] = self.font["hmtx"][alt]

def log(text):
	print(f"\033[32m{text}\033[0m")
def err(text):
	print(f"\033[31m{text}\033[0m")
