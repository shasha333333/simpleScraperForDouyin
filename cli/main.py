import logging
from core.processor import main
from core.logger import setup_logging

if __name__ == "__main__":
    setup_logging()  # 仅使用控制台和文件日志
    logging.info("=" * 50)
    logging.info("开始处理博主视频信息...")
    main()
    logging.info("处理完成!")
    logging.info("=" * 50)