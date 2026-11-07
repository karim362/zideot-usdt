window.addEventListener('load', function() {
    const tg = window.Telegram?.WebApp;
    if (tg) tg.expand();

    const BLOCK_ID = "58386"; 
    const urlParams = new URLSearchParams(window.location.search);
    let userId = tg?.initDataUnsafe?.user?.id || urlParams.get('user_id');
    
    let currentBalance = parseFloat(urlParams.get('balance') || 0.0000000);
    let refsCount = parseInt(urlParams.get('refs') || 0);
    
    const REWARD_AMOUNT = 0.1;

    function updateUI() {
        const balanceEl = document.getElementById('balance');
        if (balanceEl) balanceEl.innerText = currentBalance.toFixed(7);
    }

    updateUI();

    async function fetchBalanceFromServer() {
        if (!userId) return;
        try {
            const response = await fetch(`https://zideot-usdt-2.onrender.com/api/get_user/${userId}`);
            const data = await response.json();
            if (data.status === 'success') {
                currentBalance = data.balance;
                refsCount = data.referrals;
                updateUI();
            }
        } catch (e) {}
    }

    fetchBalanceFromServer();

    const watchAdBtn = document.getElementById('watchAdBtn');
    const showBalanceBtn = document.getElementById('showBalanceBtn');
    const showRefsBtn = document.getElementById('showRefsBtn');
    const withdrawBtn = document.getElementById('withdrawBtn');
    const statusMessage = document.getElementById('statusMessage');

    if (showBalanceBtn) showBalanceBtn.addEventListener('click', () => tg.showAlert(`💎 رصيدك الحالي: ${currentBalance.toFixed(7)} USDT`));
    
    if (showRefsBtn) {
        showRefsBtn.addEventListener('click', () => {
            tg.showPopup({
                title: 'إحالاتي 👥',
                message: `عدد إحالاتك: ${refsCount}\n\nكل 10 إحالات = 1.0000000 USDT`,
                buttons: [{type: 'ok'}]
            });
        });
    }

    if (withdrawBtn) {
        withdrawBtn.addEventListener('click', () => {
            if (currentBalance < 10.0) {
                tg.showPopup({
                    title: 'تحتاج المزيد! 💎',
                    message: `الحد الأدنى للسحب هو 10.0000000 USDT.\nرصيدك الحالي: ${currentBalance.toFixed(7)} USDT\n\nاستمر في مشاهدة الإعلانات لجمع المزيد!`,
                    buttons: [{type: 'ok'}]
                });
            } else {
                const wallet = prompt("💳 يرجى إدخال عنوان محفظة USDT (TRC20 أو ERC20) الخاصة بك:");
                if (wallet && wallet.length > 20) {
                    fetch('https://zideot-usdt-2.onrender.com/api/withdraw', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user_id: userId, wallet: wallet })
                    }).then(res => res.json()).then(data => {
                        if (data.status === 'success') {
                            tg.showAlert("✅ تم استلام طلبك!\nسيتم تحويل المبلغ إلى محفظتك في غضون بضع ساعات.");
                            currentBalance -= 10.0;
                            updateUI();
                        } else {
                            tg.showAlert("❌ حدث خطأ: " + data.message);
                        }
                    }).catch(e => tg.showAlert("❌ فشل الاتصال بالسيرفر"));
                } else if (wallet) {
                    tg.showAlert("⚠️ عنوان المحفظة غير صحيح. يرجى المحاولة مرة أخرى.");
                }
            }
        });
    }

    if (watchAdBtn) {
        watchAdBtn.addEventListener('click', () => {
            if (!window.Adsgram) return;
            const AdController = window.Adsgram.init({ blockId: BLOCK_ID });

            watchAdBtn.disabled = true;
            if(statusMessage) statusMessage.innerText = "جاري تحميل الإعلان...";

            AdController.show()
                .then((result) => {
                    currentBalance += REWARD_AMOUNT;
                    updateUI();
                    if(statusMessage) statusMessage.innerText = `🎉 مبروك! تمت الإضافة.`;
                    watchAdBtn.disabled = false;

                    fetch('https://zideot-usdt-2.onrender.com/api/add_points', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user_id: userId, amount: REWARD_AMOUNT })
                    }).catch(e => console.log(e));
                })
                .catch((result) => {
                    if(statusMessage) statusMessage.innerText = "⚠️ لم تكمل مشاهدة الإعلان.";
                    watchAdBtn.disabled = false;
                });
        });
    }
});
