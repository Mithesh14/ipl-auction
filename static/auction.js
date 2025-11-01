// Initialize Socket.IO connection
const socket = io();

let currentUser = null;
let auctionState = null;
let categories = [];
let lastAnnouncedPlayerName = null; // Track last player announced to avoid duplicate messages
let lastBidIds = new Set(); // Track bid IDs to avoid duplicate bid messages
let announcedUsers = new Set(); // Track users who have been announced as joined/left

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadUserInfo();
    await loadCategories();
    setupEventListeners();
    setupSocketListeners();
    
    // Auto-refresh auction state every 1 second
    setInterval(async () => {
        if (auctionState && auctionState.status === 'active') {
            try {
                // Request current auction state from server
                socket.emit('get_auction_state');
            } catch (error) {
                console.error('Error refreshing auction state:', error);
            }
        }
    }, 1000);
});

async function loadUserInfo() {
    try {
        const res = await fetch('/api/user-info');
        if (res.ok) {
            currentUser = await res.json();
            document.getElementById('user-name').textContent = currentUser.team_name;
            updatePurse();
            
            // Show/hide admin buttons
            const isAdmin = currentUser.username.toLowerCase() === 'mithesh';
            const sellBtn = document.getElementById('sell-player-btn');
            if (sellBtn) {
                sellBtn.style.display = isAdmin ? 'inline-block' : 'none';
            }
            
            // Hide category selector if not admin
            const categorySelector = document.getElementById('category-selector');
            if (categorySelector && !isAdmin) {
                const grid = categorySelector.querySelector('#category-grid');
                if (grid) {
                    grid.style.display = 'none';
                }
            }
        } else {
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Error loading user info:', error);
        window.location.href = '/';
    }
}

async function loadCategories() {
    try {
        const res = await fetch('/api/init', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            categories = data.categories;
            renderCategoryGrid(data.category_info);
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

function renderCategoryGrid(categoryInfo) {
    const grid = document.getElementById('category-grid');
    if (!grid) return; // Not admin, grid doesn't exist
    
    grid.innerHTML = '';
    
    // Check if auction is active
    const isActive = auctionState && auctionState.status === 'active' && auctionState.active_pool;
    const activePool = auctionState?.active_pool || '';
    
    categories.forEach(category => {
        if (!categoryInfo[category]) return;
        
        const info = categoryInfo[category];
        const card = document.createElement('div');
        card.className = 'category-card';
        
        // Check if this pool is active
        const pool1Key = `${category}_1`;
        const pool2Key = `${category}_2`;
        const pool1Active = activePool === pool1Key;
        const pool2Active = activePool === pool2Key;
        
        card.innerHTML = `
            <h3>${category}</h3>
            <div class="set-info">Set 1: ${info.set1_count} players</div>
            <div class="set-info">Set 2: ${info.set2_count} players</div>
            ${pool1Active ? '<div class="pool-status active">🟢 IN PROGRESS</div>' : ''}
            ${pool2Active ? '<div class="pool-status active">🟢 IN PROGRESS</div>' : ''}
            <button class="btn-primary ${isActive && !pool1Active ? 'disabled' : ''}" 
                    style="margin-top: 10px; width: 100%;" 
                    ${isActive && !pool1Active ? 'disabled' : ''}
                    onclick="selectCategory('${category}', 1)">
                ${pool1Active ? '⏸️ In Progress' : '🎯 Start Set 1'}
            </button>
            <button class="btn-primary ${isActive && !pool2Active ? 'disabled' : ''}" 
                    style="margin-top: 5px; width: 100%;" 
                    ${isActive && !pool2Active ? 'disabled' : ''}
                    onclick="selectCategory('${category}', 2)">
                ${pool2Active ? '⏸️ In Progress' : '🎯 Start Set 2'}
            </button>
        `;
        grid.appendChild(card);
    });
    
    // Show active pool message
    if (isActive && auctionState.current_category) {
        showActivePoolMessage();
    }
}

function showActivePoolMessage() {
    const selector = document.getElementById('category-selector');
    if (!selector) return;
    
    let existingMsg = selector.querySelector('.active-pool-message');
    if (!existingMsg) {
        existingMsg = document.createElement('div');
        existingMsg.className = 'active-pool-message';
        selector.insertBefore(existingMsg, selector.querySelector('#category-grid'));
    }
    
    existingMsg.innerHTML = `
        <div class="info-banner">
            <span class="info-icon">ℹ️</span>
            <div class="info-content">
                <strong>Auction In Progress:</strong> ${auctionState.current_category} - Set ${auctionState.current_set}
                <br><small>Complete or pause the current auction before starting a new pool.</small>
            </div>
        </div>
    `;
}

function selectCategory(category, set) {
    socket.emit('start_auction', {
        action: 'start',
        category: category,
        set: set
    });
}

// Socket event listeners
function setupSocketListeners() {
    socket.on('connect', () => {
        console.log('Connected to auction room');
    });

    socket.on('auction_state', (state) => {
        const previousPlayerName = auctionState?.current_player?.name;
        auctionState = state;
        
        // Only update display if player actually changed
        const currentPlayerName = auctionState?.current_player?.name;
        if (previousPlayerName !== currentPlayerName) {
            updateAuctionDisplay();
        } else {
            // Just update bids/highest bid without re-announcing player
            if (auctionState && auctionState.current_player) {
                updateBidsList(auctionState.current_player.name);
                const bids = auctionState.bids[auctionState.current_player.name] || [];
                const highest = bids.length > 0 ? Math.max(...bids.map(b => b.amount)) : 0;
                updateHighestBid(highest);
            }
        }
        
        // Re-render category grid to update button states if admin
        if (currentUser && currentUser.username.toLowerCase() === 'mithesh') {
            fetch('/api/init', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        renderCategoryGrid(data.category_info);
                    }
                })
                .catch(err => console.error('Error refreshing categories:', err));
        }
    });

    socket.on('auction_error', (data) => {
        alert(data.message || 'An error occurred');
    });

    socket.on('new_bid', (data) => {
        // Only add to feed if this is a genuinely new bid (not from auto-refresh)
        // The new_bid event is emitted from server only when a real bid happens
        addBidToFeed(data);
        updateBidsList(data.player_name);
        if (auctionState && auctionState.current_player && 
            auctionState.current_player.name === data.player_name) {
            updateHighestBid(data.highest_bid);
        }
    });

    socket.on('player_sold', (data) => {
        addSaleToFeed(data);
        // Update My Team for the buyer
        if (currentUser && data.buyer === currentUser.username) {
            updateMyTeam();
        }
        // Update purse for all users (they need to see updated purchases)
        updatePurse();
        // Also update My Team purchases list (shows in right panel)
        updateMyTeam();
    });

    socket.on('bid_error', (data) => {
        showBidStatus(data.message, 'error');
    });

    socket.on('user_connected', (data) => {
        // Only show join message once per user
        const userKey = `joined_${data.username}`;
        if (!announcedUsers.has(userKey)) {
            addFeedMessage(`${data.username} joined the auction`, 'info');
            announcedUsers.add(userKey);
            // Remove from left set if they had left before
            announcedUsers.delete(`left_${data.username}`);
        }
    });

    socket.on('user_disconnected', (data) => {
        // Only show leave message once per user
        const userKey = `left_${data.username}`;
        if (!announcedUsers.has(userKey)) {
            addFeedMessage(`${data.username} left the auction`, 'info');
            announcedUsers.add(userKey);
            // Remove from joined set so they can rejoin later
            announcedUsers.delete(`joined_${data.username}`);
        }
    });

    socket.on('pool_started', (data) => {
        addFeedMessage(
            `🎯 <strong>AUCTION STARTED!</strong> ${data.category} - Set ${data.set} is now active. Get ready to bid!`,
            'info'
        );
        // Refresh category grid if admin
        if (currentUser && currentUser.username.toLowerCase() === 'mithesh') {
            setTimeout(() => loadCategories(), 500);
        }
    });
}

function updateAuctionDisplay() {
    if (!auctionState || !auctionState.current_player) {
        document.getElementById('category-selector').style.display = 'block';
        document.getElementById('current-player-section').style.display = 'none';
        lastAnnouncedPlayerName = null; // Reset when no player is on block
        return;
    }

    document.getElementById('category-selector').style.display = 'none';
    document.getElementById('current-player-section').style.display = 'block';

    const player = auctionState.current_player;
    const lotNum = auctionState.current_player_index + 1;
    
    document.getElementById('lot-number').textContent = lotNum;
    document.getElementById('current-player-name').textContent = player.name;
    document.getElementById('base-price').textContent = player.base_price || '0.00';
    
    // Update category display
    const category = getPlayerCategory(player.name) || auctionState.current_category || 'N/A';
    document.getElementById('player-category').textContent = category;
    
    const bids = auctionState.bids[player.name] || [];
    const highest = bids.length > 0 ? Math.max(...bids.map(b => b.amount)) : 0;
    updateHighestBid(highest);
    updateBidsList(player.name);
    
    // Add player announcement to feed ONLY if this is a new player
    if (lastAnnouncedPlayerName !== player.name) {
        addFeedMessage(
            `🎯 <strong>LOT #${lotNum}</strong> - <strong>${player.name}</strong> is now on the block! Base Price: ₹${player.base_price || '0.00'} Cr`,
            'info'
        );
        lastAnnouncedPlayerName = player.name;
    }
}

function updateHighestBid(amount) {
    const elem = document.getElementById('highest-bid');
    elem.textContent = amount.toFixed(2) + ' Cr';
}

function updateBidsList(playerName) {
    const container = document.getElementById('bids-container');
    const bids = (auctionState.bids[playerName] || []).slice().reverse(); // Show all bids, newest first
    
    container.innerHTML = '';
    if (bids.length === 0) {
        container.innerHTML = '<div class="no-bids"><p>No bids placed yet. Be the first to bid!</p></div>';
        return;
    }

    // Show all bids with timestamps
    bids.forEach((bid, index) => {
        const div = document.createElement('div');
        div.className = 'bid-item';
        
        // Format timestamp
        const bidTime = bid.timestamp ? new Date(bid.timestamp) : new Date();
        const timeStr = bidTime.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        
        // Highlight if this is the current highest bid
        const isHighest = index === 0;
        if (isHighest) {
            div.classList.add('highest-bid');
        }
        
        div.innerHTML = `
            <div class="bid-header">
                <span class="bid-number">Bid #${bids.length - index}</span>
                <span class="bid-time">${timeStr}</span>
            </div>
            <div class="bid-details">
                <span class="bidder-name">${bid.team_name}</span>
                <span class="bid-amount">₹${bid.amount.toFixed(2)} Cr</span>
            </div>
            ${isHighest ? '<div class="leading-badge">👑 LEADING</div>' : ''}
        `;
        container.appendChild(div);
    });
}

function addBidToFeed(data) {
    const bidTime = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    addFeedMessage(
        `💰 <strong>${data.bid.team_name}</strong> placed a bid of <strong>₹${data.bid.amount.toFixed(2)} Cr</strong> for <strong>${data.player_name}</strong> <span class="feed-time">[${bidTime}]</span>`,
        'bid'
    );
    
    // Update bids list for current player if it's the active player
    if (auctionState && auctionState.current_player && 
        auctionState.current_player.name === data.player_name) {
        updateBidsList(data.player_name);
    }
}

function addSaleToFeed(data) {
    const saleTime = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    addFeedMessage(
        `🎯 <strong>SOLD!</strong> ${data.player_name} → <strong>${data.team_name}</strong> for <strong>₹${data.price.toFixed(2)} Cr</strong> <span class="feed-time">[${saleTime}]</span>`,
        'sold'
    );
}

function addFeedMessage(message, type = 'info') {
    const feed = document.getElementById('live-feed-content');
    const div = document.createElement('div');
    div.className = `feed-item ${type}`;
    div.innerHTML = message; // Use innerHTML to support HTML tags
    feed.insertBefore(div, feed.firstChild);
    
    // Smooth scroll to top
    feed.scrollTop = 0;
    
    // Limit to 100 items
    if (feed.children.length > 100) {
        feed.removeChild(feed.lastChild);
    }
}

function setupEventListeners() {
    // Place bid button
    document.getElementById('place-bid-btn').addEventListener('click', placeBid);
    document.getElementById('bid-amount').addEventListener('keypress', e => {
        if (e.key === 'Enter') placeBid();
    });

    // Next player button (admin only)
    const nextPlayerBtn = document.getElementById('next-player-btn');
    if (nextPlayerBtn) {
        nextPlayerBtn.addEventListener('click', () => {
            if (currentUser && currentUser.username.toLowerCase() === 'mithesh') {
                socket.emit('next_player');
            }
        });
    }

    // Sell player button
    const sellBtn = document.getElementById('sell-player-btn');
    if (sellBtn) {
        sellBtn.addEventListener('click', () => {
            if (auctionState && auctionState.current_player) {
                if (confirm(`Sell ${auctionState.current_player.name} to highest bidder?`)) {
                    socket.emit('sell_player', {
                        player_name: auctionState.current_player.name
                    });
                }
            }
        });
    }

    // Player info button
    document.getElementById('player-info-btn').addEventListener('click', showPlayerInfo);

    // My team modal
    document.getElementById('my-team-btn').addEventListener('click', () => {
        document.getElementById('team-modal').classList.add('active');
        updateMyTeam();
    });

    document.getElementById('close-team-modal').addEventListener('click', () => {
        document.getElementById('team-modal').classList.remove('active');
    });

    // Back to pool button
    document.getElementById('back-to-pool-btn').addEventListener('click', () => {
        // Only allow going back if we're the admin and auction is not active
        // OR if we want to pause/reset the current player view
        if (auctionState && auctionState.current_player) {
            // For admin: ask if they want to pause/go back
            if (currentUser && currentUser.username.toLowerCase() === 'mithesh') {
                if (confirm('Go back to pool selection? The current player will remain on block until you continue.')) {
                    // Just hide the player view locally - server state remains
                    document.getElementById('category-selector').style.display = 'block';
                    document.getElementById('current-player-section').style.display = 'none';
                    lastAnnouncedPlayerName = null; // Reset so if we come back, it re-announces
                }
            } else {
                // For non-admin: just hide the view
                document.getElementById('category-selector').style.display = 'block';
                document.getElementById('current-player-section').style.display = 'none';
            }
        } else {
            // No player on block, safe to show category selector
            document.getElementById('category-selector').style.display = 'block';
            document.getElementById('current-player-section').style.display = 'none';
        }
    });

    // Logout
    document.getElementById('logout-btn').addEventListener('click', async () => {
        await fetch('/logout');
        window.location.href = '/';
    });

    // Close modals on outside click
    window.addEventListener('click', (e) => {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
}

function placeBid() {
    const amount = parseFloat(document.getElementById('bid-amount').value);
    if (!amount || amount <= 0) {
        showBidStatus('Please enter a valid bid amount', 'error');
        return;
    }

    if (!auctionState || !auctionState.current_player) {
        showBidStatus('No player currently on auction', 'error');
        return;
    }

    socket.emit('place_bid', {
        player_name: auctionState.current_player.name,
        amount: amount
    });

    document.getElementById('bid-amount').value = '';
    showBidStatus('Bid placed...', 'info');
}

function showBidStatus(message, type) {
    const status = document.getElementById('bid-status');
    status.textContent = message;
    status.style.color = type === 'error' ? 'var(--danger)' : 
                         type === 'success' ? 'var(--success)' : 'var(--text-light)';
    setTimeout(() => {
        status.textContent = '';
    }, 3000);
}

async function showPlayerInfo() {
    if (!auctionState || !auctionState.current_player) return;

    const modal = document.getElementById('player-info-modal');
    const content = document.getElementById('player-info-content');
    const nameEl = document.getElementById('modal-player-name');
    
    nameEl.textContent = auctionState.current_player.name;
    content.innerHTML = 'Loading player information...';
    modal.classList.add('active');

    try {
        const res = await fetch(`/api/player-info/${encodeURIComponent(auctionState.current_player.name)}`);
        const data = await res.json();
        
        if (data.success) {
            const info = data.info;
            content.innerHTML = `
                <div style="text-align: center; margin-bottom: 20px;">
                    ${info.image_url ? `<img src="${info.image_url}" style="max-width: 200px; border-radius: 10px;">` : ''}
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>Category:</strong> ${get_player_category(auctionState.current_player.name) || 'N/A'}<br>
                    <strong>Base Price:</strong> ${auctionState.current_player.base_price || '0.00'} Cr
                </div>
                ${info.description ? `<p style="margin-bottom: 15px;">${info.description}</p>` : ''}
                ${info.birth_info ? `<div><strong>Birth:</strong> ${info.birth_info}</div>` : ''}
                ${info.nationality ? `<div><strong>Nationality:</strong> ${info.nationality}</div>` : ''}
                ${info.external_links && info.external_links.cricinfo ? 
                    `<div style="margin-top: 15px;"><a href="${info.external_links.cricinfo}" target="_blank">View on ESPN Cricinfo</a></div>` : ''}
            `;
        } else {
            content.innerHTML = '<p>Error loading player information</p>';
        }
    } catch (error) {
        content.innerHTML = '<p>Error loading player information</p>';
    }
}

document.getElementById('close-info-modal').addEventListener('click', () => {
    document.getElementById('player-info-modal').classList.remove('active');
});

async function updateMyTeam() {
    try {
        const res = await fetch('/api/my-team');
        if (!res.ok) {
            console.error('Failed to fetch team data:', res.status);
            return;
        }
        const data = await res.json();
        
        // Debug logging
        console.log('My Team API Response:', data);
        console.log('Players count:', data.players ? data.players.length : 0);
        if (data.players && data.players.length > 0) {
            console.log('Sample player:', data.players[0]);
        }
        
        // Update purchases list (right panel - "My Purchases")
        const purchasesList = document.getElementById('purchases-list');
        if (purchasesList) {
            purchasesList.innerHTML = '';
            
            if (!data.players || data.players.length === 0) {
                purchasesList.innerHTML = '<p style="color: var(--text-light);">No players purchased yet</p>';
            } else {
                data.players.forEach(player => {
                    const div = document.createElement('div');
                    div.className = 'purchase-item';
                    div.innerHTML = `
                        <span class="player-name">${player.name}</span>
                        <span class="price">${player.price.toFixed(2)} Cr</span>
                    `;
                    purchasesList.appendChild(div);
                });
            }
        }

    // Always update playing 11 in modal when data is available
    updatePlaying11(data.players || []);
        
        // Update purse summary
        const totalSpentEl = document.getElementById('total-spent');
        const remainingPurseEl = document.getElementById('remaining-purse');
        if (totalSpentEl && data.total_spent !== undefined) {
            totalSpentEl.textContent = data.total_spent.toFixed(2);
        }
        if (remainingPurseEl && data.purse_remaining !== undefined) {
            remainingPurseEl.textContent = data.purse_remaining.toFixed(2);
        }
    } catch (error) {
        console.error('Error updating team:', error);
    }
}

function updatePlaying11(players) {
    const container = document.getElementById('playing-11-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    // If no players, show message
    if (!players || players.length === 0) {
        container.innerHTML = '<div style="text-align: center; color: var(--text-light); padding: 20px;">No players in your team yet</div>';
        // Also clear all players list
        const allContainer = document.getElementById('all-players-container');
        if (allContainer) {
            allContainer.innerHTML = '<div style="text-align: center; color: var(--text-light); padding: 20px;">No players purchased</div>';
        }
        return;
    }
    
    // Sort players by position
    const sorted = [...players].sort((a, b) => (a.position || 999) - (b.position || 999));
    
    // Get captain (position 1 is typically captain, but we'll check)
    const captainPosition = sorted.find(p => p.is_captain)?.position || 1;
    
    for (let i = 1; i <= 11; i++) {
        const player = sorted.find(p => p.position === i);
        const div = document.createElement('div');
        div.className = 'player-card-draggable';
        div.dataset.position = i;
        
        if (player) {
            const isForeign = player.is_foreign || false;
            const isCaptain = i === captainPosition || player.is_captain;
            
            div.innerHTML = `
                <div class="player-icons">
                    ${isForeign ? '<span class="foreign-icon" title="Foreign Player">✈️</span>' : ''}
                    ${isCaptain ? '<span class="captain-icon" title="Captain">⭐</span>' : ''}
                </div>
                <strong>${player.name}</strong>
                <div class="position">Position ${i}</div>
                <div class="player-badges">
                    ${isForeign ? '<span class="badge foreign-badge">Foreign</span>' : '<span class="badge indian-badge">Indian</span>'}
                    ${isCaptain ? '<span class="badge captain-badge">Captain</span>' : ''}
                </div>
            `;
            div.draggable = true;
            div.dataset.playerName = player.name;
            div.dataset.isForeign = isForeign;
            div.addEventListener('dragstart', handleDragStart);
        } else {
            div.innerHTML = `
                <div style="color: var(--text-light);">Position ${i}</div>
                <div class="position">Drag player here</div>
            `;
        }
        
        div.addEventListener('dragover', handleDragOver);
        div.addEventListener('drop', handleDrop);
        div.addEventListener('click', (e) => {
            if (player && e.target.closest('.player-card-draggable')) {
                toggleCaptain(i, player.name);
            }
        });
        
        container.appendChild(div);
    }

    // Add all players list
    const allContainer = document.getElementById('all-players-container');
    if (!allContainer) return; // Safety check
    allContainer.innerHTML = '';
    sorted.forEach(player => {
        const div = document.createElement('div');
        div.className = 'player-item';
        div.draggable = true;
        div.dataset.playerName = player.name;
        div.dataset.isForeign = player.is_foreign || false;
        
        const isForeign = player.is_foreign || false;
        div.innerHTML = `
            <span>${player.name}</span>
            ${isForeign ? '<span class="foreign-indicator">✈️</span>' : '<span class="indian-indicator">🇮🇳</span>'}
        `;
        div.addEventListener('dragstart', handleDragStart);
        allContainer.appendChild(div);
    });
}

function toggleCaptain(position, playerName) {
    // Double-click or special button to set captain
    // For now, position 1 is captain
    // This could be enhanced with a right-click menu or button
}

let draggedElement = null;

function handleDragStart(e) {
    draggedElement = this;
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

async function handleDrop(e) {
    e.preventDefault();
    if (!draggedElement || !draggedElement.dataset.playerName) return;

    const position = parseInt(this.dataset.position);
    const playerName = draggedElement.dataset.playerName;

    // Update playing 11
    try {
        const players = [];
        let captainName = null;
        
        document.querySelectorAll('#playing-11-container .player-card-draggable').forEach((card, idx) => {
            const name = card.dataset.playerName;
            const pos = parseInt(card.dataset.position);
            if (name) {
                players.push({ name, position: pos || idx + 1 });
                // First position or marked as captain
                if (pos === 1 || card.querySelector('.captain-icon')) {
                    captainName = name;
                }
            }
        });

        // Add the dropped player at this position
        if (!players.find(p => p.name === playerName && p.position === position)) {
            players.push({ name: playerName, position });
        }
        
        // Position 1 is default captain if no captain set
        if (position === 1) {
            captainName = playerName;
        }

        await fetch('/api/update-playing-11', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ players, captain: captainName })
        });

        updateMyTeam();
    } catch (error) {
        console.error('Error updating playing 11:', error);
    }
}

async function updatePurse() {
    try {
        const res = await fetch('/api/user-info');
        if (res.ok) {
            const user = await res.json();
            const teamRes = await fetch('/api/my-team');
            if (teamRes.ok) {
                const team = await teamRes.json();
                document.getElementById('my-purse').textContent = team.purse_remaining.toFixed(2);
            }
        }
    } catch (error) {
        console.error('Error updating purse:', error);
    }
}

// Helper function to get player category
function getPlayerCategory(name) {
    if (!auctionState || !auctionState.current_category) return null;
    return auctionState.current_category;
}

