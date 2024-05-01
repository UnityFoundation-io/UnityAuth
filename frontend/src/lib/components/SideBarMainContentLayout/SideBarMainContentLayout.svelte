<div class="layout-container">
	<aside class="side-bar h-full">
		<slot name="side-bar" />
	</aside>
	<div class="main-content"><slot name="main-content" /></div>
</div>

<style>
	.layout-container {
		height: 100%;
		display: grid;
		grid-template-columns: 400px auto;
	}
	.main-content {
		flex-grow: 1;
		height: 100%;
	}

	.side-bar {
		position: relative;
		width: 400px;
	}

	aside {
		overflow-y: auto;
	}
</style>
