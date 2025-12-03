# Nintendo Play Activity OCR

Scripts that run [EasyOCR](https://pypi.org/project/easyocr) and post-process screenshots
taken from the “Play Activity” section of the
new “Nintendo Store” mobile app. For an unknown reason, this app provides
uniquely fine-grained data about “Play Activity” including historical
dates and durations for games associated with a Nintendo account.

How to build the container and run the script:

```shell
docker build . -t nintendo-play-activity-ocr
python index.py
```

Using CPU for the OCR is fine for this use-case, as the images
are small, few in number, and only run once. The result is
an SQLite database (`nintendo-play-activity-ocr.sqlite`)
that can be queried:

```sql
SELECT game_name, SUM(duration) AS d FROM sessions
WHERE STRFTIME('%Y', date) = '2025' AND game_system = 'Switch'
GROUP BY game_name ORDER BY d DESC;
```

| Game Name           | Duration |
|---------------------|----------|
| Mario Kart World    | 37500    |
| Kirby Air Riders    | 24000    |
| Super Mario Odyssey | 17100    |
| Pikmin 2            | 8400     |
| Pikmin 4            | 3900     |

## License

CC BY-NC-SA 4.0
