import razorpay

RAZORPAY_KEY_ID = "rzp_test_T1RKD9TKwPOir8"
RAZORPAY_KEY_SECRET = "MB0Plca24O3UchMUeMgFW1s8"

client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)