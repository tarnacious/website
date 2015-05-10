def import_posts():
    from app import importer
    import sys
    importer.import_posts(sys.argv[1])

if __name__ == "__main__":
    import_posts()
