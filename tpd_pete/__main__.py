from tpd_pete.pete import Pete
import tpd_pete


def main():
	""" Start TPD Pete
	"""
	p = Pete()
	p.start()


if __name__ == "__main__":
	print("TPD Deployment - Project Pete - v%s" % tpd_pete.VERSION)
	main()
